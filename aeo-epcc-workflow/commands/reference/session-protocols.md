# Session Protocols

Shared session startup, resume, and progress tracking patterns for EPCC commands.

## Session Startup Protocol

### Phase 1: Getting Oriented (REQUIRED)

Before ANY implementation, run automatic orientation:

```bash
# 1. Confirm working directory
pwd

# 2. Check git state
git branch --show-current
git status --short
git log --oneline -10

# 3. Read progress state (if exists)
if [ -f "epcc-progress.md" ]; then
    head -100 epcc-progress.md
fi

# 4. Read feature list (if exists)
if [ -f "epcc-features.json" ]; then
    cat epcc-features.json
fi

# 5. Check for init.sh requirement from TRD
if grep -q "init.sh required.*Yes" TECH_REQ.md 2>/dev/null; then
    if [ ! -f "init.sh" ] || [ "TECH_REQ.md" -nt "init.sh" ]; then
        echo "TRD requires init.sh - generating/regenerating..."
    else
        echo "Found init.sh - run if servers need starting"
    fi
elif [ -f "init.sh" ]; then
    echo "Found init.sh (manual) - run if servers need starting"
fi
```

**Announce session context:**
```
Session [N] starting. Progress: X/Y features (Z%).
Last session: [summary from epcc-progress.md]
Resuming: [feature name from arguments or highest-priority incomplete]
```

### Phase 2: Regression Verification

Before new work, verify existing features still work:

```bash
# Run test suite (use project's test command)
npm test  # or pytest, cargo test, etc.
```

**If any previously-passing features now fail:**
- **FIX REGRESSIONS FIRST** before new work
- Update `epcc-features.json`: Set `passes: false` for regressed features
- Document regression in `epcc-progress.md`

### Phase 3: Feature Selection

**One Feature at a Time Rule:**

1. If feature specified in arguments: Work on that feature
2. If no feature specified: Select highest-priority feature where `passes: false`
3. Work on ONE feature until verified
4. Complete ALL subtasks before moving to next feature

**Anti-pattern**: Implementing multiple features before any verification
**Correct pattern**: Implement → Verify → Commit → Next Feature

## Session Resume Detection

**On entry**, check for existing session state:

### Step 1: Check for Progress File
```
if epcc-progress.md exists:
    Parse last exploration session for this area
```

### Step 2: Detect Prior Work
```python
for session in epcc_progress.sessions:
    if session.phase == current_phase and session.target matches ARGUMENTS:
        age = days_since(session.timestamp)
        if age < 7:
            trigger_reuse_prompt(session)
```

### Step 3: Offer Reuse Option (If Applicable)
If prior work found within 7 days, use AskUserQuestion:
```json
{
  "questions": [{
    "question": "Prior work for this area found from [date]. How do you want to proceed?",
    "header": "Prior Found",
    "multiSelect": false,
    "options": [
      {"label": "Use existing", "description": "Load prior findings, skip re-work"},
      {"label": "Start fresh", "description": "Full re-work from scratch (overwrites existing)"},
      {"label": "Refresh delta", "description": "Quick check for changes since last session"}
    ]
  }]
}
```

### Step 4: Handle Response
- **Use existing**: Load existing output, present summary, ask for next steps
- **Start fresh**: Proceed with normal flow
- **Refresh delta**: Run `git diff --stat [last_commit]..HEAD` to identify changed files, work only those

## Checkpoint Commits

After completing each feature:

```bash
# 1. Stage implementation files + state files
git add [implementation files]
git add epcc-features.json epcc-progress.md

# 2. Commit with feature reference
git commit -m "feat(F00X): [feature description] - E2E verified

- [What was implemented]
- All acceptance criteria verified
- Tests passing

Refs: epcc-features.json#F00X"

# 3. Push if remote exists
git push
```

## Session Handoff

Before ending session (or on context exhaustion):

**If feature incomplete:**
```bash
git add -A
git commit -m "wip(F00X): [current state]

Session [N] progress:
- [What was done]
- [What remains]

HANDOFF: [specific instructions for next session]
Resume at: [file:line] - [what to do next]"
```

**Update epcc-progress.md:**
```markdown
---

## Session [N]: [Date Time]

### Summary
[What was accomplished]

### Feature Progress
- F00X: [status] ([X/Y subtasks], [specific state])

### Work Completed
- [Completed item 1]
- [Completed item 2]

### Files Modified
- [file1.ts] - [what was changed]
- [file2.ts] - [what was changed]

### Checkpoint Commit
[SHA]: [message]

### Handoff Notes
**Resume at**: [file:line]
**Next action**: [specific instruction]
**Blockers**: [None / description]

### Next Session
[What should happen next]

---
```

**"IT IS CATASTROPHIC TO LOSE PROGRESS" - always document before ending**

## Quality Assurance Protocol

**"Test like a human user with mouse and keyboard. Don't take shortcuts."**

- For web features: Use browser automation (Chrome DevTools MCP)
- Take screenshots to verify visual correctness
- Check for: contrast issues, layout problems, console errors
- Run complete user workflows end-to-end

**Only when ALL acceptance criteria verified:**
- Update `epcc-features.json`: `"passes": true`, `"status": "verified"`
- Check all subtasks as complete
- Add test evidence (screenshot path or test output)
- Add timestamp: `"verifiedAt": "[ISO timestamp]"`

**NEVER edit feature definitions - only modify:**
- `passes` field
- `status` field
- `subtasks[].status` field
- `verifiedAt` field
- `commit` field

## Session Protocol Summary

| Phase | Action | Outcome |
|-------|--------|---------|
| 1. Orient | pwd, git, progress, features | Know current state |
| 2. Verify | Run tests | Catch regressions |
| 3. Select | Pick one feature | Focus, no context switching |
| 4. Validate | E2E testing | Verify before marking done |
| 5. Commit | Checkpoint commit | Save verified progress |
| 6. Handoff | Document for next session | Enable continuity |
