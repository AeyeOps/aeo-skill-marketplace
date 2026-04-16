---
name: aeo-continuation-prompt
version: 0.1.0
description: Generate a paste-ready continuation prompt that captures current task state, so a fresh session after /clear can resume without losing the thread
argument-hint: "[focus area]"
disable-model-invocation: true
---

# Continuation Prompt Generator

<purpose>
Long sessions accumulate context that stops earning its weight — exploration
dead-ends, tool output, abandoned approaches. At some point a fresh start is
cheaper than carrying the whole history forward. This command produces a brief
you can paste into a new session after `/clear` so the next Claude picks up
where this one left off — with what it needs, not what it doesn't.
</purpose>

<focus>
$ARGUMENTS

If a focus is given (e.g. "the release push", "the GCM install"), scope the
prompt to that thread and drop unrelated detours. If empty, capture the whole
active task.
</focus>

<what_the_next_session_needs>
A continuation prompt works when the receiving session can act without
re-asking the user. The following typically earn their place:

- The current task in one sentence, with enough context to understand why it
  matters — because a task without motivation invites second-guessing
- Decisions already made and approaches already ruled out, so the new session
  doesn't re-litigate them
- Current concrete state: relevant file paths, branch, unpushed work,
  background processes, anything that would surprise a fresh reader
- The next specific action (file to edit, command to run), not a vague "continue"
- Non-obvious constraints discovered this session — environment quirks, tool
  bugs, user preferences — because these would otherwise have to be rediscovered
- What is explicitly out of scope, when the scope is easy to misread

These are guidance, not a checklist. Include what applies; skip what doesn't.
</what_the_next_session_needs>

<format>
Plain prose in a single code fence, ready to paste verbatim. Refer to files by
absolute path. Quote exact commands when the next action is to run something.
Leave out this session's debugging chatter and tool output — distill to what
the next session needs to succeed.

Length calibrates to task complexity. A one-file fix needs a short prompt; a
multi-component refactor needs more. Longer than the task warrants is worse
than shorter, because a bloated prompt rebuilds the bloat you're trying to escape.
</format>

<output>
Return only the continuation prompt inside a single code fence. Skip preamble
and closing remarks so the user can copy the fence cleanly.
</output>
