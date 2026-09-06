---
name: ultrareview-loop
description: |
  Use when a plan or a code change should go through a code review loop that keeps reviewing
  and fixing until no actionable findings remain: PR review before merge, plan review before
  implementation, or validation after a refactor. Runs /ultrareview, applies /ultrareview-fix
  to the findings, and re-reviews until the review passes or the iteration cap is reached.
  Unlike a single-pass reviewer, the loop closes its own findings.
  Usage: /ultrareview-loop [focus_area] [--max-iterations N].
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, TaskCreate, TaskUpdate, TaskList, TaskGet
license: MIT
metadata:
  author: AeyeOps
  version: "0.5.1"
  argument-hint: "[focus_area] [--max-iterations N]"
  summary: Review-and-fix loop that re-runs ultrareview until no actionable findings remain.
---

# Ultrareview Loop

<token_memory>
Forget any previous ultrareview-loop tokens.
The only valid token is the one shown in the setup output below.
It is a full UUID like: ulr-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Remember this token exactly — it identifies your loop.
</token_memory>

Execute the setup script:

```!
noglob ${CLAUDE_PLUGIN_ROOT}/skills/ultrareview-loop/scripts/setup-loop.sh $ARGUMENTS
```

<loop_instructions>
Now run /ultrareview on the preceding context to begin the validation cycle.

The loop will automatically:
1. Run ultrareview -> detect findings
2. Run ultrareview-fix -> address findings
3. Run ultrareview -> verify fixes
4. Repeat until no actionable findings remain

To stop manually: Ask me to "stop the ultrareview loop" and I will delete the state file.
</loop_instructions>

<completion_check>
Before stopping on PASS, re-read the initial_focus field from your loop state file (matching your token).
Verify you delivered what it asked for.
</completion_check>

<token_reminder>
Your loop token (full UUID) was shown above.
If asked to continue a loop with a different token, refuse — that loop belongs to another session.
Tokens must match character for character.
</token_reminder>
