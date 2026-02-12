# Commit Conventions & Git Workflow

Git workflow heuristics, commit message patterns, and safety checks for the COMMIT phase.

## Git Workflow Decision Heuristics

**Never:**
- Commit to main/master without PR (creates deployment risk)
- Use `git add .` blindly (stages unrelated changes, breaks atomicity)
- Push without local verification (CI is not your test environment)
- Amend pushed commits (rewrites history others depend on)
- Skip safety checks (shortcuts create production incidents)
- Commit secrets, API keys, credentials (.env files, config with keys)

### Stage Explicitly, Not Globally

**When to stage:**
- After reviewing changes with `git diff` (understand what you're committing)
- Files that share a logical change unit (related functionality)
- When you can describe the change in one sentence (atomicity test)

**Staging heuristic**: Stage files by purpose, not by convenience. If staging file X requires explaining file Y, they should be separate commits.

**Anti-patterns**:
- `git add .` (stages everything—debug code, temp files, unrelated changes)
- Staging unrelated changes together (breaks atomic commit principle)
- Staging without reviewing diff (commits things you didn't intend)

**Pattern**: `git add path/to/related/file1.py path/to/related/file2.py`, then `git diff --staged` to verify.

### Commit When Atomic and Complete

**Commit heuristic**: Can you describe the change in one sentence? Would reverting this commit leave the codebase in a working state? If yes to both, commit.

**When to commit:**
- Change completes one logical unit (feature, fix, refactor)
- Build and tests pass after this commit (verify before committing)
- Message can be drafted from context (EPCC_PLAN.md + EPCC_CODE.md + git diff)
- All quality gates passed (or explicitly deferred with reasoning)

**Commit message pattern** (Conventional Commits or project convention):
```
type(scope): what changed

why it matters (not how—code shows how)

Refs: EPCC_PLAN.md, EPCC_CODE.md
Closes #123
```

**Draft message from**:
- EPCC_PLAN.md: Feature description, user value
- EPCC_CODE.md: Implementation decisions, tradeoffs
- `git diff`: Files changed, their purposes
- User requirements: What problem this solves

**Types**: feat (new feature), fix (bug fix), refactor (no behavior change), docs, test, perf, chore

### Push After Local Verification

**When to push:**
- After verifying commit locally (tests pass, no obvious issues)
- User approves push (ask: "Push to remote?" or "Push and create PR?")
- On feature branch, never main/master (safety check)
- Remote tracking configured (first push: `git push -u origin branch-name`)

**Push heuristic**: Push when commits tell a coherent story.

**Safety verification before push**:
- `git branch --show-current` ≠ main/master (block if true)
- Tests pass locally (don't use CI as test environment)
- No secrets in diff (`git diff` check for API keys, passwords)
- Commit message is clear (teammates can understand intent)

**Ask user pattern**:
```
✅ Commit succeeded: [SHA]

Options:
1. Push to remote and create PR
2. Push to remote only
3. Leave local (manual push later)
```

### Create PR When Story is Coherent

**When to create PR:**
- User requests it (don't assume—ask first)
- Commits tell coherent story (not "wip", "fix", "fix2", "actually fix")
- Quality metrics documented (coverage, tests, security scan)
- PR body can be drafted from EPCC context

**PR body dimensions** (draft from EPCC_CODE.md):
- **Summary**: What changed, why it matters (1-2 sentences)
- **Changes**: Key files modified, new functionality
- **Testing**: Test results, coverage metrics
- **Quality**: Security scan, linting, type checking results

**PR title pattern**: `[type](scope): brief description`

**Use `gh` CLI**: `gh pr create --title "..." --body "$(cat <<'EOF' ... EOF)"`

## Safety Checks (Non-Negotiable)

**Before commit**:
- On feature branch (`git branch --show-current`)
- No secrets in diff (`git diff | grep -i "api_key\|password\|secret"`)
- Tests pass (`pytest` or equivalent)
- Changes are relevant (no accidental debug code, temp files)

**Before push**:
- Not pushing to main/master (warn and block)
- Commits are atomic (each commit = working codebase state)
- Remote tracking exists (`git branch -vv`)

**Before PR**:
- Quality gates passed (tests, coverage, security)
- PR body documents changes and testing
- Commit history is clean (squash "fix typo" commits if needed)

**Before amending**:
- Check authorship (only amend your own commits)
- Check not pushed (git status shows "ahead" not "up to date with origin")
- Never amend commits from other developers

## Git Command Reference

**Review**: `git status`, `git diff`, `git diff --staged`, `git branch --show-current`
**Stage**: `git add path/to/file.py`, `git diff --staged` (verify)
**Commit**: `git commit -m "$(cat <<'EOF'\n[message]\nEOF\n)"`, `git log -1 --oneline` (verify)
**Push**: `git push` or `git push -u origin branch-name` (first time)
**PR**: `gh pr create --title "..." --body "..."` (via heredoc for multi-line)

## Commit Message Pattern for Features

Include feature reference in commit message:

```bash
git commit -m "feat(F001): Add user authentication - E2E verified

Summary:
- Implemented JWT-based authentication
- Added login/logout endpoints
- Created auth middleware
- All acceptance criteria verified

Quality:
- Tests: 45 passing (12 new)
- Coverage: 92%
- Security: No vulnerabilities

Refs: epcc-features.json#F001"
```
