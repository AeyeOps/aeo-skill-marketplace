---
name: epcc-code
description: Code phase of EPCC workflow - implement with confidence
version: 0.1.0
argument-hint: "[task-to-implement] [--tdd|--quick|--full]"
---

# EPCC Code Command

You are in the **CODE** phase of the Explore-Plan-Code-Commit workflow. Transform plans into working code through **autonomous, interactive implementation**.

**Opening Principle**: High-quality implementation balances autonomous progress with systematic validation, shipping confidently by making errors observable and fixes verifiable.

## Implementation Target
$ARGUMENTS

## Session Startup Protocol

If `epcc-features.json` exists, this is a tracked multi-session project. Execute the session startup protocol before implementation.

@reference/session-protocols.md

## Implementation Philosophy

**Core Principle**: Work autonomously with clear judgment. You're the main coding agent with full context and all tools. Use sub-agents for specialized tasks when they add value.

### Implementation Modes

Parse mode from arguments and adapt your approach:
- **`--tdd`**: Tests-first development (write tests → implement → verify)
- **`--quick`**: Fast iteration (basic tests, skip optional validators)
- **`--full`**: Production-grade (all quality gates, parallel validation)
- **Default**: Standard implementation (tests + code + docs)

**Modes differ in validation intensity**, not rigid procedures.

## Execution-First Pattern (Critical)

**Never ask questions you can answer by executing code.**

1. **Try** → Run tests, check results
2. **Fix** → Auto-fix failures (linting, formatting, simple bugs)
3. **Re-try** → Re-run tests to verify fix
4. **Iterate** → Repeat until tests pass
5. **Ask only if blocked** → Can't fix after 2-3 attempts or fix requires requirement change

**Ask when**: Requirements unclear, architecture decision needed, breaking change required, blocked after multiple fix attempts.

**Don't ask when**: Tests failed with clear error (auto-fix), linting issues (auto-fix), file locations unclear (use Grep/Glob), simple bugs (fix and verify).

## Implementation Workflow

### Phase 1: Gather Context

```bash
# Check implementation plan
if [ -f "EPCC_PLAN.md" ]; then
    # Extract: Task breakdown, technical approach, acceptance criteria
fi

# Check technical requirements
if [ -f "TECH_REQ.md" ]; then
    # Extract: Tech stack, architecture, research insights, code patterns
fi

# Check exploration findings
if [ -f "EPCC_EXPLORE.md" ]; then
    # Read: Coding patterns, testing approach, constraints
fi
```

**Autonomous context gathering** (if needed):
- **Explore**: EPCC_EXPLORE.md missing → `/epcc-explore [area] --quick`
- **Research**: Unfamiliar tech/pattern → WebSearch/WebFetch

### Phase 2: Create Task List

Use TodoWrite to track progress. Mark "in_progress" BEFORE starting, "completed" IMMEDIATELY after finishing. Only one task "in_progress" at a time.

### Phase 3: Implement

**Mode-Specific Approaches:**

- **`--tdd`**: Write failing tests → implement minimal code → refactor while green
- **`--quick`**: Implement directly → basic happy-path tests → skip optional validators
- **`--full`**: Implement with best practices → comprehensive tests → run parallel validators
- **Default**: Follow project patterns → standard test coverage → verify quality gates

### Phase 4: Test & Validate

**Simple tests**: Write yourself following project patterns from EPCC_EXPLORE.md.
**Complex tests**: Delegate to @test-generator with full context.

**Quality validation**: Tests pass → Coverage meets target → Linting clean → Type checking passes.

**Auto-fix pattern**: Run → fix → re-run → proceed when all pass.

### Phase 5: Document Implementation

Generate `EPCC_CODE.md`. See code implementation patterns below for output template.

## Specialized Sub-Agents

@reference/code-implementation-patterns.md

## Debugging Heuristics

1. **Hypothesize**: What's the likely cause? (read error message carefully)
2. **Isolate**: Reproduce in smallest context
3. **Inspect**: Add logging, check assumptions
4. **Fix**: Make smallest change that fixes root cause (not symptoms)
5. **Verify**: Re-run tests, check for side effects

## Refactoring Guidance

**Refactor immediately when**: Code duplicated 3+ times, function > 50 lines, unclear names, dead code.
**Defer refactoring when**: Working code minor cleanup, large structural changes, pattern emerges across project.

**Principle**: Leave code better than you found it, but don't let perfection block shipping.

## Quality Gates

Before marking implementation complete:

- All tests passing (run test suite)
- Coverage meets target (from EPCC_EXPLORE.md or >80% default)
- No linting errors (auto-fixed)
- Type checking passes (no type errors)
- Security scan clean (no CRITICAL/HIGH vulnerabilities)
- Documentation updated (API docs, README, inline comments)

**Don't proceed to commit phase with failing quality gates.**

## Common Pitfalls

- **Asking Instead of Executing**: Run tests, show results — don't ask "should I?"
- **Over-Delegating Simple Tasks**: Write simple tests yourself when you have context
- **Ignoring Exploration Findings**: Follow EPCC_EXPLORE.md conventions
- **Incomplete Context in Delegations**: Provide tech stack, patterns, requirements
- **Rigid Mode Following**: Modes are philosophies, not procedures

## Second-Order Convergence Warnings

Even with this guidance, you may default to:
- Following mode workflows as checklists (work autonomously instead)
- Over-using sub-agents for simple tasks (write simple tests/docs yourself)
- Writing exhaustive documentation for small changes (match detail to complexity)
- Asking permission for standard operations (execute with safety checks)
- Stopping at first test pass (verify edge cases, error handling)
- Not exploring when patterns needed (use /epcc-explore if missing)

## Remember

**Your role**: Autonomous, interactive implementation agent with full context and judgment.

**Work pattern**: Gather context → Execute → Fix → Verify → Document. Ask only when blocked.

**Sub-agents**: Helpers for specialized tasks with complete, self-contained context.

**Quality**: Tests pass, coverage met, security clean, docs updated before commit.

**Ready to implement. Run `/epcc-commit` when quality gates pass.**
