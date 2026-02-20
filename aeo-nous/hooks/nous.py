#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pydantic>=2.0",
# ]
# ///
"""
Nous: Context Compaction + Self-Improvement System

Dual-purpose hook entry point:

SessionStart (sync): Injects context (recent learnings/knowledge) via stdout.
Stop (async): Flushes inboxes, fires extraction subprocesses at thresholds.
  Blocking decision (>65% context) handled by nous-stop-guard.sh (sync).
"""

from __future__ import annotations

import fcntl
import json
import logging
import os
import re
import subprocess
import sys
import time
from logging.handlers import RotatingFileHandler
from collections import deque
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from pydantic import BaseModel, ValidationError
except ImportError:
    # Auto-install pydantic if missing; try pip then uv
    _installed = False
    for _cmd in (
        [sys.executable, "-m", "pip", "install", "--quiet", "pydantic>=2.0"],
        ["uv", "pip", "install", "--quiet", "pydantic>=2.0"],
    ):
        try:
            subprocess.check_call(_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            _installed = True
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    if not _installed:
        print("nous: pydantic is required but could not be installed. "
              "Run: pip install pydantic>=2.0", file=sys.stderr)
        sys.exit(1)
    from pydantic import BaseModel, ValidationError

if TYPE_CHECKING:
    from lenses.base import ExtractionLens
    from lenses.models import StatuslineEntry


# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
LOG_PATH = Path.home() / ".claude" / "aeo-nous.log"
LOG_MAX_BYTES = 2_097_152   # 2 MB per file (generous for JSONL overhead)
LOG_BACKUP_COUNT = 3        # keep aeo-nous.log + 3 rotated files
STATUSLINE_PATH = Path.home() / ".claude" / "statusline-activity.jsonl"

# SessionStart: how many recent entries to inject from each encoded file
INJECT_RECENT_COUNT = 20

# Statusline: max lines to read (matches LOG_ROTATE_AT in statusline.sh)
STATUSLINE_MAX_LINES = 100

# ISO 8601 timestamp pattern for validation
ISO_TIMESTAMP_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$')

# Extraction: cursor file tracking last extracted timestamp per project
CURSOR_FILE = ".claude/nous/extraction_cursor.json"

# Stop hook: context window thresholds (percentage)
CONTEXT_SKIP_PCT = 10          # Below this: skip entirely
CONTEXT_EXTRACT_MAX_PCT = 60   # At or below: flush inboxes + fire extractions
                               # Above: flush only (blocking handled by nous-stop-guard.sh at 65%)

# Extraction: subprocess timeout and model
WORKER_TIMEOUT_SECONDS = 300   # 5 minutes
EXTRACTION_MODEL = "sonnet"

# Extraction: max recent entries for deduplication context
DEDUP_ENTRY_LIMIT = 20


# =============================================================================
# HookInput - Pydantic model for stdin JSON from Claude Code
# =============================================================================

class PermissionMode(str, Enum):
    DEFAULT = "default"
    PLAN = "plan"
    ACCEPT_EDITS = "acceptEdits"
    DONT_ASK = "dontAsk"
    BYPASS_PERMISSIONS = "bypassPermissions"


class SessionSource(str, Enum):
    STARTUP = "startup"
    RESUME = "resume"
    CLEAR = "clear"
    COMPACT = "compact"


class SessionStartInput(BaseModel):
    """SessionStart hook input - matches Claude Code docs"""
    session_id: str
    transcript_path: str
    cwd: str
    hook_event_name: str
    source: SessionSource
    permission_mode: PermissionMode | None = None  # Docs say required, verify in practice
    model: str | None = None  # Not always provided (e.g., resume, clear)
    agent_type: str | None = None


class StopInput(BaseModel):
    """Stop hook input - matches Claude Code docs"""
    session_id: str
    transcript_path: str
    cwd: str
    hook_event_name: str
    permission_mode: PermissionMode | None = None  # Defensive: may not always be sent
    stop_hook_active: bool


# =============================================================================
# Nous Logger - Process-safe JSONL rotating log
# =============================================================================


class _ProcessSafeRotatingHandler(RotatingFileHandler):
    """RotatingFileHandler with fcntl.flock for multi-process safety."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            with open(self.baseFilename + ".lock", "a") as lf:
                fcntl.flock(lf, fcntl.LOCK_EX)
                try:
                    super().emit(record)
                finally:
                    fcntl.flock(lf, fcntl.LOCK_UN)
        except Exception:
            self.handleError(record)


_logger: logging.Logger | None = None


def _get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = logging.getLogger("nous")
        _logger.setLevel(logging.DEBUG)
        _logger.propagate = False
        handler = _ProcessSafeRotatingHandler(
            LOG_PATH, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        _logger.addHandler(handler)
    return _logger


def log(msg: str, session: str = "?", project: str = "?",
        role: str = "hook") -> None:
    """Log a JSONL line to aeo-nous.log."""
    entry = json.dumps({
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "pid": os.getpid(),
        "sid": session[:8] if session != "?" else "?",
        "project": project,
        "role": role,
        "event": msg,
    }, separators=(",", ":"))
    _get_logger().info(entry)


def shutdown_logger() -> None:
    if _logger:
        for h in _logger.handlers:
            h.flush()


# =============================================================================
# Statusline Reader - Extract full StatuslineEntry objects
# =============================================================================

# Lazy import cache for StatuslineEntry model
_statusline_model_cache = None


def _get_statusline_model():
    """Lazy import of StatuslineEntry model."""
    global _statusline_model_cache
    if _statusline_model_cache is None:
        if str(SCRIPT_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPT_DIR))
        from lenses.models import StatuslineEntry
        _statusline_model_cache = StatuslineEntry
    return _statusline_model_cache


def parse_statusline_entry(line: str) -> "StatuslineEntry | None":
    """Parse a single statusline JSONL line into a full StatuslineEntry."""
    SE = _get_statusline_model()
    try:
        data = json.loads(line.strip())
        return SE.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        log(f"WARN parse_statusline: {type(e).__name__}", session="?", project="?")
        return None


def read_statusline_for_session(
    project_path: str,
    session_id: str,
) -> "tuple[StatuslineEntry | None, StatuslineEntry | None]":
    """
    Read statusline and find the two most recent entries for this project+session.

    Returns (current, previous) StatuslineEntry objects.
    Both may be None if no entries found.
    """
    if not STATUSLINE_PATH.exists():
        return None, None

    try:
        with open(STATUSLINE_PATH, "r") as f:
            last_lines = deque(f, maxlen=STATUSLINE_MAX_LINES)
    except OSError as e:
        log(f"ERROR read_statusline: {e}", session="?", project="?")
        return None, None

    # Walk backward to find two entries for this project+session
    session_entries: list = []
    for line in reversed(last_lines):
        entry = parse_statusline_entry(line)
        if entry and entry.cwd == project_path and entry.session_id == session_id:
            session_entries.append(entry)
            if len(session_entries) >= 2:
                break

    if not session_entries:
        return None, None

    current = session_entries[0]
    previous = session_entries[1] if len(session_entries) >= 2 else None
    return current, previous


# =============================================================================
# Timestamp Validation
# =============================================================================

def _is_valid_iso_timestamp(ts: str) -> bool:
    """Validate timestamp is ISO 8601 format to prevent shell injection."""
    return bool(ISO_TIMESTAMP_PATTERN.match(ts))


# =============================================================================
# Encoded File Reading
# =============================================================================

def read_existing_encoded(lens_encoded_path: Path, project_dir: Path, limit: int = DEDUP_ENTRY_LIMIT) -> list[dict]:
    """
    Read recent entries from encoded file (engram/cortex) for deduplication.

    Returns last N entries to avoid extracting duplicates.
    """
    encoded_file = project_dir / lens_encoded_path
    if not encoded_file.exists():
        return []

    entries = []
    try:
        with open(encoded_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError as e:
        log(f"ERROR read_encoded: {e}", session="?", project="?")
        return []

    # Return last N entries for deduplication context
    return entries[-limit:] if len(entries) > limit else entries


# =============================================================================
# Extraction Cursor - Persistent tracking of last extracted timestamp
# =============================================================================

def get_extraction_cursor(project_dir: Path) -> str:
    """
    Get cursor, creating at current time if missing or corrupt.

    Uses file locking to prevent race conditions between concurrent workers.
    """
    cursor_file = project_dir / CURSOR_FILE
    cursor_file.parent.mkdir(parents=True, exist_ok=True)

    reason = "missing"
    try:
        with open(cursor_file, "a+") as f:  # a+ creates if not exists
            fcntl.flock(f, fcntl.LOCK_EX)  # Exclusive lock (blocking)
            try:
                f.seek(0)
                content = f.read()
                if content:
                    try:
                        data = json.loads(content)
                        if ts := data.get("last_extracted_ts"):
                            return ts
                        reason = "empty"
                    except json.JSONDecodeError as e:
                        reason = f"corrupt: {e}"
                        # Fall through to reinitialize while holding lock
                # File empty, missing ts, or corrupt - initialize
                now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                f.seek(0)
                f.truncate()
                f.write(json.dumps({"last_extracted_ts": now}))
                f.flush()
                log(f"cursor_created reason={reason} ts={now}", session="?", project=str(project_dir))
                return now
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)  # Release lock
    except OSError as e:
        # Fallback for file system errors only
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        log(f"cursor_error reason={e} fallback={now}", session="?", project=str(project_dir))
        return now


def write_extraction_cursor(project_dir: Path, ts: str) -> None:
    """
    Update last_extracted_ts for this project.

    Uses file locking to prevent race conditions between concurrent workers.
    """
    if not _is_valid_iso_timestamp(ts):
        log(f"WARN cursor_invalid_ts: {ts[:30]}", session="?", project=str(project_dir))
        return  # Don't write invalid timestamps

    cursor_file = project_dir / CURSOR_FILE
    cursor_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(cursor_file, "a+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)  # Exclusive lock (blocking)
            try:
                f.seek(0)
                f.truncate()
                f.write(json.dumps({"last_extracted_ts": ts}))
                f.flush()
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)  # Release lock
    except OSError as e:
        log(f"WARN cursor_write_error: {e}", session="?", project=str(project_dir))


# =============================================================================
# SessionStart - Context Injection
# =============================================================================

def read_last_n_jsonl(path: Path, n: int) -> list[dict]:
    """Read the last N entries from a JSONL file."""
    if not path.exists():
        return []

    entries = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        return []

    return entries[-n:] if len(entries) > n else entries


def handle_session_start(hook: SessionStartInput) -> int:
    """
    Inject context at session start.

    Outputs to stdout (gets injected into Claude context):
    1. Recent learnings from engram
    2. Recent knowledge from cortex

    Note: CLAUDE.md files are NOT injected here — Claude Code loads them natively.
    """
    log(f"SESSION_START source={hook.source} model={hook.model} perm={hook.permission_mode}",
        session=hook.session_id, project=hook.cwd)

    project_dir = Path(hook.cwd)

    # Paths to encoded files
    engram_path = project_dir / ".claude/nous/learnings/engram.jsonl"
    cortex_path = project_dir / ".claude/nous/knowledge/cortex.jsonl"

    output_parts = []

    # 1. Recent learnings (engram)
    learnings = read_last_n_jsonl(engram_path, INJECT_RECENT_COUNT)
    if learnings:
        learnings_text = "\n".join(json.dumps(e) for e in learnings)
        output_parts.append(f"<recent_learnings>\n{learnings_text}\n</recent_learnings>")

    # 2. Recent knowledge (cortex)
    knowledge = read_last_n_jsonl(cortex_path, INJECT_RECENT_COUNT)
    if knowledge:
        knowledge_text = "\n".join(json.dumps(e) for e in knowledge)
        output_parts.append(f"<recent_knowledge>\n{knowledge_text}\n</recent_knowledge>")

    # 3. Instruction to share injected context
    if learnings or knowledge:
        output_parts.append("<nous_notice>Share a brief summary of the learnings and knowledge injected above so the user understands what context you received.</nous_notice>")

    # Output to stdout - this gets injected into Claude's context
    if output_parts:
        print("\n\n".join(output_parts))
        log(f"INJECTED learnings={len(learnings)} knowledge={len(knowledge)}",
            session=hook.session_id, project=hook.cwd)
    else:
        log("INJECTED nothing (no content found)", session=hook.session_id, project=hook.cwd)

    return 0


# =============================================================================
# Stop Hook - Fire-and-forget extraction (all async, no blocking)
# =============================================================================


def _fire_extraction_subprocess(
    lens: "ExtractionLens",
    current: "StatuslineEntry",
    previous: "StatuslineEntry | None",
    start_ts: str,
    end_ts: str,
    existing: list[dict],
    project_dir: Path,
) -> None:
    """
    Fire extraction subprocess - no wait, stdout goes to unique fragment file.

    Each extraction writes to inbox_path.{timestamp}_{random} to avoid races.
    flush_inbox() globs for these fragments and processes them atomically.

    The extraction agent reads the transcript file directly using the Read tool,
    filtering to entries within [start_ts, end_ts] window.
    """
    from lenses import build_extraction_prompt

    prompt = build_extraction_prompt(lens, current, previous, start_ts, end_ts, existing)

    inbox_base = project_dir / lens.inbox_path
    inbox_base.parent.mkdir(parents=True, exist_ok=True)

    # Unique fragment: inbox.jsonl.{timestamp}_{pid}_{random}
    fragment_id = f"{int(time.time())}_{os.getpid()}_{os.urandom(4).hex()}"
    fragment_file = inbox_base.parent / f"{inbox_base.name}.{fragment_id}"
    log(f"SPAWN lens={lens.name} fragment={fragment_id} prompt_bytes={len(prompt)} transcript={current.transcript_path}",
        session=current.session_id, project=current.cwd)

    # Fire and forget - stdout goes to unique fragment file
    # Use timeout(1) to kill claude if it runs too long
    # --permission-mode bypassPermissions required for Read tool in non-interactive --print mode
    with open(fragment_file, "w") as f:
        _log_fh = open(LOG_PATH, "a")
        try:
            proc = subprocess.Popen(
                ["timeout", str(WORKER_TIMEOUT_SECONDS), "claude", "--print",
                 "--no-session-persistence",
                 "--permission-mode", "bypassPermissions", "--model", EXTRACTION_MODEL, "-p", prompt],
                stdout=f,
                stderr=_log_fh,
                start_new_session=True,  # Detach from parent
                env={
                    **{k: v for k, v in os.environ.items() if k != "CLAUDECODE"},
                    "NOUS_SUBPROCESS": "1",
                    "NOUS_SESSION": current.session_id,
                    "NOUS_PROJECT": current.cwd,
                },  # Unset CLAUDECODE to prevent hook recursion in nested claude --print
            )
        except OSError:
            _log_fh.close()
            raise
        _log_fh.close()  # Popen dups the fd; closing parent copy is safe
        log(f"SPAWN_PID lens={lens.name} pid={proc.pid}", session=current.session_id, project=current.cwd)


def run_stop_hook(current: "StatuslineEntry", previous: "StatuslineEntry | None") -> None:
    """
    Stop hook: threshold-based extraction.

    Runs directly in the async hook process (hooks.json has "async": true).
    Blocking decision is handled by nous-stop-guard.sh (sync).
    Extraction subprocesses (claude --print) are fire-and-forget via Popen.
    """
    pct = current.context_window.used_percentage
    project_dir = Path(current.cwd)
    session = current.session_id
    project = current.cwd

    log(f"STOP ctx={pct}%", session=session, project=project)

    if pct < CONTEXT_SKIP_PCT:
        return

    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))

    from lenses import LEARNINGS_LENS, KNOWLEDGE_LENS, flush_inbox

    # Always flush inboxes
    learnings_flushed = flush_inbox(LEARNINGS_LENS, project_dir)
    knowledge_flushed = flush_inbox(KNOWLEDGE_LENS, project_dir)
    log(f"FLUSHED ctx={pct}% engram={learnings_flushed} cortex={knowledge_flushed}",
        session=session, project=project)

    # Fire extractions only at lower context usage
    if pct <= CONTEXT_EXTRACT_MAX_PCT:
        start_ts = get_extraction_cursor(project_dir)
        end_ts = current.meta_ts
        log(f"EXTRACT window start={start_ts} end={end_ts}", session=session, project=project)

        transcript = Path(current.transcript_path)
        if not transcript.exists():
            log(f"SKIP transcript_missing={current.transcript_path}", session=session, project=project)
            return

        existing_learnings = read_existing_encoded(LEARNINGS_LENS.encoded_path, project_dir)
        existing_knowledge = read_existing_encoded(KNOWLEDGE_LENS.encoded_path, project_dir)

        _fire_extraction_subprocess(LEARNINGS_LENS, current, previous, start_ts, end_ts, existing_learnings, project_dir)
        _fire_extraction_subprocess(KNOWLEDGE_LENS, current, previous, start_ts, end_ts, existing_knowledge, project_dir)

        write_extraction_cursor(project_dir, current.meta_ts)
        log(f"CURSOR_ADVANCED ts={current.meta_ts}", session=session, project=project)


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> int:
    """Hook entry point. Fire-and-forget, always returns 0."""
    if os.environ.get("NOUS_SUBPROCESS"):
        return 0

    start_time = datetime.now()
    session_id = "?"
    project = "?"

    try:
        stdin_data = sys.stdin.read()
        raw = json.loads(stdin_data)
        event_name = raw.get("hook_event_name", "")
        session_id = raw.get("session_id", "?")
        project = raw.get("cwd", "?")

        if event_name == "SessionStart":
            hook = SessionStartInput.model_validate(raw)
            result = handle_session_start(hook)
            total_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            log(f"END {total_ms}ms", session=session_id, project=project)
            return result

        elif event_name == "Stop":
            hook = StopInput.model_validate(raw)

            if hook.stop_hook_active:
                log("SKIP stop_hook_active", session=session_id, project=project)
                return 0

            current, previous = read_statusline_for_session(hook.cwd, hook.session_id)
            if not current:
                log(f"WARN no_statusline_entry session={session_id[:8]}", session=session_id, project=project)
                return 0

            run_stop_hook(current, previous)

            total_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            log(f"END {total_ms}ms", session=session_id, project=project)
            return 0

        else:
            log(f"SKIP unknown_event={event_name}", session=session_id, project=project)
            return 0

    except Exception as e:
        import traceback
        log(f"ERROR {type(e).__name__}: {e}", session=session_id, project=project)
        log(f"TRACEBACK {traceback.format_exc()[:500]}", session=session_id, project=project)
        return 0  # Best-effort: don't block on error

    finally:
        shutdown_logger()


if __name__ == "__main__":
    sys.exit(main())
