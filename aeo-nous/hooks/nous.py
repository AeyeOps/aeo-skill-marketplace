#!/usr/bin/env python3
"""
Nous: Context Compaction + Self-Improvement System

Dual-purpose hook entry point:

SessionStart: Injects context (CLAUDE.md files + recent learnings/knowledge)
Stop: Monitors context usage, extracts learnings/knowledge at thresholds

SessionStart outputs to stdout (injected into Claude context).
Stop runs silently - logs to nous.log.
"""

from __future__ import annotations

import fcntl
import json
import os
import queue
import re
import subprocess
import sys
import multiprocessing
import threading
from collections import deque
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, ValidationError

if TYPE_CHECKING:
    from lenses.base import ExtractionLens
    from lenses.models import StatuslineEntry


# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
LOG_PATH = Path.home() / ".claude" / "nous.log"
STATUSLINE_PATH = Path.home() / ".claude" / "statusline-activity.jsonl"

# SessionStart: how many recent entries to inject from each encoded file
INJECT_RECENT_COUNT = 5

# Statusline: max lines to read (matches LOG_ROTATE_AT in statusline.sh)
STATUSLINE_MAX_LINES = 100

# ISO 8601 timestamp pattern for validation
ISO_TIMESTAMP_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$')

# Extraction: cursor file tracking last extracted timestamp per project
CURSOR_FILE = ".claude/nous/extraction_cursor.json"


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
    permission_mode: Optional[PermissionMode] = None  # Docs say required, verify in practice
    model: Optional[str] = None  # Not always provided (e.g., resume, clear)
    agent_type: Optional[str] = None


class StopInput(BaseModel):
    """Stop hook input - matches Claude Code docs"""
    session_id: str
    transcript_path: str
    cwd: str
    hook_event_name: str
    permission_mode: Optional[PermissionMode] = None  # Defensive: may not always be sent
    stop_hook_active: bool


# =============================================================================
# Nous Logger - Async, non-blocking logging (separate from statusline)
# =============================================================================

_log_queue: queue.Queue[Optional[str]] = queue.Queue()
_log_thread: Optional[threading.Thread] = None
_log_started = False


def _log_worker() -> None:
    """Background thread that writes log messages to file."""
    with open(LOG_PATH, "a") as f:
        while True:
            msg = _log_queue.get()
            if msg is None:
                break
            f.write(msg + "\n")
            f.flush()


def _ensure_log_thread() -> None:
    """Start the log worker thread if not already running."""
    global _log_thread, _log_started
    if not _log_started:
        _log_thread = threading.Thread(target=_log_worker, daemon=True)
        _log_thread.start()
        _log_started = True


def log(msg: str, session: str = "?", project: str = "?") -> None:
    """
    Log a message asynchronously to nous.log.

    Format: yyMMddHHMMSS.mmm session project_path message
    """
    _ensure_log_thread()
    ts = datetime.now().strftime("%y%m%d%H%M%S.%f")[:17]  # yyMMddHHMMSS.mmm
    _log_queue.put(f"{ts} {session} {project} {msg}")


def shutdown_logger() -> None:
    """Gracefully shutdown the logger thread."""
    if _log_started:
        _log_queue.put(None)
        if _log_thread:
            _log_thread.join(timeout=1.0)


def reset_logger_for_subprocess() -> None:
    """Reset logger state for use in forked subprocess."""
    global _log_thread, _log_started, _log_queue
    _log_thread = None
    _log_started = False
    # Create fresh queue - parent's queue isn't usable after fork
    _log_queue = queue.Queue()


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

def read_existing_encoded(lens_encoded_path: Path, project_dir: Path, limit: int = 20) -> list[dict]:
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
    import time

    from lenses import build_extraction_prompt

    prompt = build_extraction_prompt(lens, current, previous, start_ts, end_ts, existing)

    inbox_base = project_dir / lens.inbox_path
    inbox_base.parent.mkdir(parents=True, exist_ok=True)

    # Unique fragment: inbox.jsonl.{timestamp}_{pid}_{random}
    fragment_id = f"{int(time.time())}_{os.getpid()}_{os.urandom(4).hex()}"
    fragment_file = inbox_base.parent / f"{inbox_base.name}.{fragment_id}"
    error_file = inbox_base.parent / f"{inbox_base.name}.{fragment_id}.stderr"

    log(f"SPAWN lens={lens.name} fragment={fragment_id} prompt_bytes={len(prompt)} transcript={current.transcript_path}",
        session=current.session_id, project=current.cwd)

    # Fire and forget - stdout goes to unique fragment file
    # Use timeout(1) to kill claude if it runs too long
    # --permission-mode bypassPermissions required for Read tool in non-interactive --print mode
    with open(fragment_file, "w") as f, open(error_file, "w") as ef:
        proc = subprocess.Popen(
            ["timeout", str(WORKER_TIMEOUT_SECONDS), "claude", "--print",
             "--permission-mode", "bypassPermissions", "--model", "opus", "-p", prompt],
            stdout=f,
            stderr=ef,
            start_new_session=True,  # Detach from parent
            env={
                **os.environ,
                "NOUS_SUBPROCESS": "1",
                "NOUS_SESSION": current.session_id,
                "NOUS_PROJECT": current.cwd,
            },  # Prevent hook recursion
        )
        log(f"SPAWN_PID lens={lens.name} pid={proc.pid}", session=current.session_id, project=current.cwd)


def _stop_hook_worker(
    current: "StatuslineEntry",
    previous: "StatuslineEntry | None",
    pct: int,
    project_dir: Path,
) -> None:
    """
    Background worker for Stop hook - does all blocking I/O in subprocess.

    Runs in separate process (survives parent exit), logs errors but never raises.
    """
    # Reset logger for subprocess - parent's thread doesn't survive fork
    reset_logger_for_subprocess()

    session = current.session_id
    project = current.cwd

    try:
        log(f"WORKER started ctx={pct}% pid={os.getpid()}", session=session, project=project)

        if str(SCRIPT_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPT_DIR))

        from lenses import LEARNINGS_LENS, KNOWLEDGE_LENS, flush_inbox
        log("WORKER lenses imported", session=session, project=project)

        if pct < 70:
            # 10-70%: Flush inboxes + fire extractions
            learnings_flushed = flush_inbox(LEARNINGS_LENS, project_dir)
            knowledge_flushed = flush_inbox(KNOWLEDGE_LENS, project_dir)
            log(f"WORKER flushed engram={learnings_flushed} cortex={knowledge_flushed}",
                session=session, project=project)

            start_ts = get_extraction_cursor(project_dir)
            end_ts = current.meta_ts
            log(f"WORKER extraction window start={start_ts} end={end_ts}", session=session, project=project)

            # Pre-flight check: verify transcript exists before spawning subprocesses
            transcript = Path(current.transcript_path)
            if not transcript.exists():
                log(f"WORKER skip_extraction transcript_missing={current.transcript_path}", session=session, project=project)
                shutdown_logger()
                return

            existing_learnings = read_existing_encoded(LEARNINGS_LENS.encoded_path, project_dir)
            existing_knowledge = read_existing_encoded(KNOWLEDGE_LENS.encoded_path, project_dir)
            log(f"WORKER existing learnings={len(existing_learnings)} knowledge={len(existing_knowledge)}", session=session, project=project)

            log(f"WORKER spawning learnings+knowledge ctx={pct}%", session=session, project=project)
            _fire_extraction_subprocess(LEARNINGS_LENS, current, previous, start_ts, end_ts, existing_learnings, project_dir)
            _fire_extraction_subprocess(KNOWLEDGE_LENS, current, previous, start_ts, end_ts, existing_knowledge, project_dir)
            log(f"WORKER spawned start={start_ts} end={end_ts}", session=session, project=project)

            # Advance cursor only after successful spawn
            write_extraction_cursor(project_dir, current.meta_ts)
            log(f"WORKER cursor_advanced ts={current.meta_ts}", session=session, project=project)

        elif pct < 85:
            # 70-85%: Only flush inboxes (no new extractions)
            learnings_flushed = flush_inbox(LEARNINGS_LENS, project_dir)
            knowledge_flushed = flush_inbox(KNOWLEDGE_LENS, project_dir)
            log(f"WORKER flush ctx={pct}% engram={learnings_flushed} cortex={knowledge_flushed}",
                session=session, project=project)

        else:
            # >= 85%: Just flush (JSON response handled by main hook, not worker)
            learnings_flushed = flush_inbox(LEARNINGS_LENS, project_dir)
            knowledge_flushed = flush_inbox(KNOWLEDGE_LENS, project_dir)
            log(f"WORKER flush_critical ctx={pct}% engram={learnings_flushed} cortex={knowledge_flushed}",
                session=session, project=project)

        log(f"WORKER complete ctx={pct}% pid={os.getpid()}", session=session, project=project)

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log(f"WORKER error: {type(e).__name__}: {e}", session=session, project=project)
        log(f"WORKER traceback: {tb[:500]}", session=session, project=project)

    finally:
        shutdown_logger()


WORKER_TIMEOUT_SECONDS = 300  # 5 minutes


def run_stop_hook(current: "StatuslineEntry", previous: "StatuslineEntry | None") -> Optional[dict]:
    """
    Stop hook: fire-and-forget threshold-based extraction.

    All work runs in background subprocess - survives parent exit.
    Returns JSON response dict for >=85% (blocks Claude, recommends /clear).

    Thresholds:
    < 10%:  Skip (context too low)
    10-70%: Flush inboxes + fire extractions
    70-85%: Flush inboxes only (context too full for new prompts)
    >= 85%: Flush + block Claude with /clear recommendation
    """
    pct = current.context_window.used_percentage
    project_dir = Path(current.cwd)

    # Entry log - always
    log(f"STOP ctx={pct}%", session=current.session_id, project=current.cwd)

    if pct < 10:
        return None

    # Fire worker subprocess - survives parent exit, self-terminates after timeout
    worker = multiprocessing.Process(
        target=_stop_hook_worker,
        args=(current, previous, pct, project_dir),
    )
    worker.start()

    log(f"DISPATCHED ctx={pct}% wpid={worker.pid}", session=current.session_id, project=current.cwd)

    # At >=85%, return JSON to block Claude and recommend /clear
    # Note: Stop hooks use top-level fields, not hookSpecificOutput
    if pct >= 85:
        return {
            "decision": "block",
            "reason": (
                f"Context at {pct}%. Run /clear (not /compact) to start fresh. "
                "Learnings have been extracted and will be injected automatically.\n\n"
                "Optional: Before clearing, ask Claude for a concise continuation prompt "
                "that captures current task state - copy it, /clear, then paste to resume."
            )
        }

    return None


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

            response = run_stop_hook(current, previous)

            # Output JSON response if hook returned one (>=85% case)
            if response:
                print(json.dumps(response))
                log(f"BLOCK_CLEAR ctx={current.context_window.used_percentage}%",
                    session=session_id, project=project)

            total_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            log(f"END {total_ms}ms", session=session_id, project=project)
            return 0  # Exit 0 required for JSON processing

        else:
            log(f"SKIP unknown_event={event_name}", session=session_id, project=project)
            return 0

    except Exception as e:
        log(f"ERROR {type(e).__name__}: {e}", session=session_id, project=project)
        return 0  # Best-effort: don't block on error

    finally:
        shutdown_logger()


if __name__ == "__main__":
    sys.exit(main())
