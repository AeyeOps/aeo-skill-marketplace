"""
Nous Lens Framework - Base Infrastructure

Provides ExtractionLens dataclass and sync helpers for fire-and-forget extraction.
"""

from __future__ import annotations

import fcntl
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Type

# Minimum age (seconds) for fragment files before processing
# Allows subprocess time to finish writing
FRAGMENT_MIN_AGE_SECONDS = 2

if TYPE_CHECKING:
    from pydantic import BaseModel
    from .models import StatuslineEntry


@dataclass
class ExtractionLens:
    """
    A lens defines a perspective for observing session transcripts.

    Each lens specifies:
    - What to look for (prompt)
    - Where to store raw extractions (inbox_path)
    - Where reviewed entries graduate to (encoded_path)
    - The schema for extracted entries
    """

    name: str  # "learnings", "knowledge", ...
    prompt: str  # Extraction instructions
    inbox_path: Path  # Where subprocess writes (relative to project)
    encoded_path: Path  # Where flush moves entries (relative to project)
    schema: Type["BaseModel"]  # Pydantic model for entries


def parse_jsonl(text: str) -> list[dict]:
    """
    Parse JSONL text, skipping invalid lines.

    Returns list of parsed dict entries.
    """
    entries = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def build_extraction_prompt(
    lens: ExtractionLens,
    current: "StatuslineEntry",
    previous: "StatuslineEntry | None",
    start_ts: str,
    end_ts: str,
    existing: list[dict],
) -> str:
    """Build the full prompt for claude --print extraction."""
    return f"""{lens.prompt}

<session_context>
  <session_id>{current.session_id}</session_id>
  <project>{current.cwd}</project>
  <start_ts>{start_ts}</start_ts>
  <end_ts>{end_ts}</end_ts>
  <model>{current.model.display_name}</model>
  <context_used_pct>{current.context_window.used_percentage}</context_used_pct>
</session_context>

<transcript_instructions>
You're extracting insights from a Claude Code session transcript. The transcript is the full conversation and can be thousands of lines, so extract only the window you need.

FILE: {current.transcript_path}
WINDOW: {start_ts} to {end_ts}

Extract this window with jq (the file is JSONL with a timestamp field per line):
jq -c 'select(.timestamp >= "{start_ts}" and .timestamp <= "{end_ts}")' "{current.transcript_path}"

Analyze the extracted content for the task above.
</transcript_instructions>

<existing_entries>
{json.dumps(existing, indent=2)}
</existing_entries>"""


def flush_inbox(lens: ExtractionLens, project_dir: Path) -> int:
    """
    Move inbox entries to encoded file (engram/cortex).

    Processes inbox fragment files (inbox_path.*) written by extraction subprocesses.
    Each fragment is read, parsed, appended to encoded, then deleted.
    No locking needed - each fragment is processed exactly once.
    Returns total number of entries flushed.
    """
    inbox_base = project_dir / lens.inbox_path
    encoded_file = project_dir / lens.encoded_path

    # Find all inbox fragment files: inbox.jsonl.* (e.g., inbox.jsonl.1706812345_abc123)
    # Excludes .stderr files which are handled separately
    inbox_dir = inbox_base.parent
    inbox_pattern = inbox_base.name + ".*"

    if not inbox_dir.exists():
        return 0

    all_fragments = list(inbox_dir.glob(inbox_pattern))
    # Separate JSONL fragments from stderr files
    fragment_files = [f for f in all_fragments if not f.name.endswith('.stderr')]
    stderr_files = [f for f in all_fragments if f.name.endswith('.stderr')]

    if not fragment_files and not stderr_files:
        return 0

    total_flushed = 0
    encoded_file.parent.mkdir(parents=True, exist_ok=True)

    now = int(time.time())

    for fragment in fragment_files:
        try:
            # Parse timestamp from fragment name: inbox.jsonl.{timestamp}_{pid}_{random}
            # Skip fragments that are too recent (subprocess may still be writing)
            fragment_suffix = fragment.name.split(".")[-1]  # e.g., "1706812345_123_abc123"
            try:
                fragment_ts = int(fragment_suffix.split("_")[0])
                age_seconds = now - fragment_ts
                if age_seconds < FRAGMENT_MIN_AGE_SECONDS:
                    continue  # Too recent, skip for now
            except (ValueError, IndexError):
                age_seconds = -1  # Unknown age

            # Read fragment content
            content = fragment.read_text().strip()

            # Also check for corresponding stderr file
            stderr_file = fragment.parent / (fragment.name + ".stderr")
            stderr_content = ""
            if stderr_file.exists():
                try:
                    stderr_content = stderr_file.read_text().strip()
                except OSError:
                    pass

            if not content:
                # Log if stderr has content (extraction may have failed)
                if stderr_content:
                    preview = stderr_content[:150].replace('\n', ' ')
                    print(f"[nous] empty fragment {fragment.name} stderr: {preview}", file=sys.stderr)
                fragment.unlink()
                if stderr_file.exists():
                    stderr_file.unlink()
                continue

            entries = parse_jsonl(content)
            if not entries:
                # Log dropped content (truncated) before deleting
                preview = content[:100].replace('\n', ' ')
                print(f"[nous] dropped invalid fragment {fragment.name}: {preview}...", file=sys.stderr)
                if stderr_content:
                    stderr_preview = stderr_content[:100].replace('\n', ' ')
                    print(f"[nous]   stderr: {stderr_preview}", file=sys.stderr)
                fragment.unlink()
                if stderr_file.exists():
                    stderr_file.unlink()
                continue

            # Append to encoded file
            with encoded_file.open("a") as ef:
                fcntl.flock(ef.fileno(), fcntl.LOCK_EX)  # Lock for append
                try:
                    for entry in entries:
                        ef.write(json.dumps(entry) + "\n")
                finally:
                    fcntl.flock(ef.fileno(), fcntl.LOCK_UN)

            # Delete fragment and stderr after successful write
            fragment.unlink()
            if stderr_file.exists():
                stderr_file.unlink()
            total_flushed += len(entries)

        except (OSError, FileNotFoundError):
            # Fragment may have been processed by another agent - skip
            continue

    # Clean up orphaned stderr files (older than 5 minutes)
    for stderr in stderr_files:
        try:
            # Parse timestamp: inbox.jsonl.{timestamp}_{pid}_{random}.stderr
            parts = stderr.name.replace('.stderr', '').split(".")
            if len(parts) >= 2:
                ts_part = parts[-1].split("_")[0]
                stderr_ts = int(ts_part)
                if now - stderr_ts > 300:  # 5 minutes
                    stderr.unlink()
        except (ValueError, IndexError, OSError):
            pass

    return total_flushed
