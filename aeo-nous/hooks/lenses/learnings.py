"""
Nous Lens: Learnings

Extracts behavioral learnings from session transcripts.
Learnings are behavioral deltas -- not facts about the project,
but changes in how to approach work.

Core question: "What should future Claude sessions do differently
because of what happened here?"
"""

from __future__ import annotations

from pathlib import Path

from .base import ExtractionLens
from .models import LearningSignal


LEARNINGS_PROMPT = """\
Analyze the transcript content from session_context.start_ts through session_context.end_ts.

The transcript is not embedded here - you must extract it from the session file.
See <transcript_instructions> below for the file path and how to extract only the relevant window.

What should future Claude sessions do differently because of what happened in this window?

Only extract learnings relevant to the project at the path in <project>. If session work touched
files, tools, or systems outside this project's directory tree, those learnings are out of scope
even if they occurred during this session. The project store should only contain guidance that
helps future sessions working on THIS project.

Learnings are behavioral deltas — actionable guidance that changes how future sessions approach work.

NOT learnings — out of scope for this lens:
- CLI flag reference information (what flags exist, what values they accept)
- System behavior descriptions (how a tool/script/hook works internally)
- Bug reports that state what IS wrong without stating what to DO about it
- Architecture facts (what components exist, how they connect)
- Path/version/config inventories

Look for:
- Errors and workarounds: Tool failures that led to successful alternatives
- Missing guidance: Issues caused by incomplete instructions
- Approach changes: a method that should REPLACE a previous default — state what to do now
- Edge case workarounds: an unexpected behavior that requires a DIFFERENT APPROACH going forward
- Corrections: User redirected Claude's approach
- Rules: User stated a principle beyond this task

Each entry should be expressible as an imperative: "do X", "avoid Y", "prefer X over Y",
"when X happens, do Y". If the entry reads as a declarative statement — "X is Y", "X does
not support Y", "X uses Y" — it is out of scope for this lens.

Use your judgment. An emphatic correction is worth capturing. Repeated subtle preferences definitely are. If something represents a genuine learning, capture it.

If the session completed smoothly with no errors, workarounds, or corrections—return nothing. Don't force learnings where none exist.

Skip duplicates of existing_entries.

For suggested_target, prefer specific locations over CLAUDE.md:
- commands/*.md for workflow gaps
- skills/**/*.md for workflow patterns
- CLAUDE.md only if it doesn't fit elsewhere (fallback)

OUTPUT FORMAT (STRICT - NO EXCEPTIONS):
- Found learnings? → Output JSONL lines, one per entry
- Found nothing? → Output NOTHING (literally zero characters, empty response)
- NEVER output prose, explanations, summaries, or markdown
- NEVER explain why you output nothing - just output nothing
- NEVER output "No learnings found" or similar messages

If you output anything other than valid JSONL or empty, you have failed the task.

Use session_context values for session and ts fields.

{"ts": "end_ts", "project": "/full/path/from/cwd", "session": "session_id", "content": "actionable guidance", "context": "why", "suggested_target": "/full/path/file.md"}"""


LEARNINGS_LENS = ExtractionLens(
    name="learnings",
    prompt=LEARNINGS_PROMPT,
    inbox_path=Path(".claude/nous/learnings/inbox.jsonl"),
    encoded_path=Path(".claude/nous/learnings/engram.jsonl"),
    schema=LearningSignal,
)
