"""
Nous Knowledge Lens

Extracts cumulative project knowledge from session transcripts.
Knowledge represents facts about the codebase - what exists and how it works.

The core question: "What facts about this project should future Claude sessions know?"
"""

from __future__ import annotations

from pathlib import Path

from .base import ExtractionLens
from .models import KnowledgeSignal


KNOWLEDGE_PROMPT = """\
Analyze the transcript content from session_context.start_ts through session_context.end_ts.

The transcript is not embedded here - you must extract it from the session file.
See <transcript_instructions> below for the file path and how to extract only the relevant window.

What facts about this project should future Claude sessions know?

Knowledge = what exists (architecture, patterns, domain concepts, dependencies, gotchas).
Learnings = how to work (captured by the other lens).

Use your judgment. Non-obvious discoveries save future investigation time.

If nothing interesting was discovered about the project, output nothing (empty response).

Skip duplicates of existing_entries.

OUTPUT FORMAT (STRICT - NO EXCEPTIONS):
- Found knowledge? → Output JSONL lines, one per entry
- Found nothing? → Output NOTHING (literally zero characters, empty response)
- NEVER output prose, explanations, summaries, or markdown
- NEVER explain why you output nothing - just output nothing
- NEVER output "No knowledge found" or similar messages

If you output anything other than valid JSONL or empty, you have failed the task.

Use session_context values for session and ts fields.

{"ts": "end_ts", "project": "/full/path/from/cwd", "session": "session_id", "category": "1-2 words", "content": "freeform prose", "context": "why it matters", "suggested_target": "/full/path/file.md"}"""


KNOWLEDGE_LENS = ExtractionLens(
    name="knowledge",
    prompt=KNOWLEDGE_PROMPT,
    inbox_path=Path(".claude/nous/knowledge/inbox.jsonl"),
    encoded_path=Path(".claude/nous/knowledge/cortex.jsonl"),
    schema=KnowledgeSignal,
)
