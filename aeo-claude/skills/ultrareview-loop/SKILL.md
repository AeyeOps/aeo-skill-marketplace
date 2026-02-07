---
name: ultrareview-loop
description: |
  Automated ultrareview validation loop that cycles between review and fix phases until
  no actionable findings remain. Use when you want continuous validation with automatic
  fix iterations on plans or code changes.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, TaskCreate, TaskUpdate, TaskList, TaskGet
model: claude-opus-4-6
hooks:
  Stop:
    - matcher: ""
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/skills/ultrareview-loop/scripts/loop-hook.sh"
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
${CLAUDE_PLUGIN_ROOT}/skills/ultrareview-loop/scripts/setup-loop.sh $ARGUMENTS
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
