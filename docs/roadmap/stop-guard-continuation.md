# Stop Guard Continuation Prompt — Improvement Roadmap

## Problem
The current stop guard message asks the user to manually request a continuation prompt from Claude, copy it, `/clear`, then paste it. This is 4 manual steps — most users will just `/clear` and lose context.

## Current flow
1. Guard fires at >80% context
2. Message says "ask Claude for a continuation prompt"
3. User asks Claude to generate one
4. User copies the prompt
5. User runs `/clear`
6. User pastes the prompt

## Proposed flow
1. Guard fires at >80% context
2. Guard message tells Claude to write continuation to a file
3. Claude writes `.claude/nous/continuation.md`
4. User runs `/clear`
5. SessionStart hook detects `continuation.md`, injects it, deletes the file

## Implementation considerations

### Option A: Instruction-based (simplest)
Change the guard message to instruct Claude directly:
```
Before clearing, write a continuation prompt to .claude/nous/continuation.md that captures:
- What was being worked on
- What's done and what's pending
- Key file paths and uncommitted changes
- Next steps

Then run /clear.
```
SessionStart checks for `continuation.md`, prepends it, deletes it after injection.

**Pros**: No code changes beyond guard message and SessionStart injection
**Cons**: Claude may not follow the instruction (it's a block message, not a prompt)

### Option B: Stop hook generates it
Add logic to nous.py Stop handler: when context >80%, use `last_assistant_message` + statusline data to generate a minimal continuation file.

**Pros**: Automatic, no user or Claude action needed
**Cons**: `last_assistant_message` alone is insufficient for a good continuation prompt. Would need transcript access which is expensive at high context.

### Option C: PreCompact hook
Hook into the PreCompact event (fires before auto-compact) to save state. But this only helps when auto-compact is enabled, not when the guard fires.

### Option D: Hybrid — guard instructs, SessionStart injects
- Guard block message includes explicit instruction to save continuation
- SessionStart checks for `continuation.md` and injects if present
- Continuation file is deleted after injection (one-shot)
- `.claude/nous/continuation.md` added to `.gitignore`

This is Option A with the injection plumbing. Most practical.

## Quality of continuation prompts
At 80%+ context, Claude has full session history and produces high-quality summaries. The structured format should include:
- Active task description
- Completed vs pending items
- Uncommitted file changes
- Key decisions made
- Explicit next steps

## Open questions
- Should the continuation file survive multiple `/clear` cycles or be consumed once?
- Should SessionStart inject it as system context or as a user-visible message?
- How to handle multiple projects with continuation files?
- Should we template the continuation format in the guard message?
