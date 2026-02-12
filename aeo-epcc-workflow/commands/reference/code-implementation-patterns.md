# Code Implementation Patterns

Sub-agent delegation patterns, init.sh templates, and error handling for the CODE phase.

## Sub-Agent Delegation Patterns

### Context Isolation Warning

**CRITICAL**: Sub-agents don't have conversation history or EPCC docs access. Each delegation must be self-contained with:
- Tech stack and project context
- Files to review (with descriptions)
- Patterns from EPCC_EXPLORE.md
- Requirements from EPCC_PLAN.md
- Clear deliverable expected

### Test Generation Delegation

```markdown
@test-generator [Clear task description]

Context:
- Project: [type and tech stack]
- Framework: [testing framework from EPCC_EXPLORE.md]
- Patterns: [fixture/mock patterns, example test to follow]

Requirements (from EPCC_PLAN.md):
- [Functional requirements to test]
- [Edge cases and error scenarios]

Files to test:
- [path/to/file.ts]: [What this file does]
- [path/to/another.ts]: [What this file does]

Deliverable: [What you expect back - test suite with X coverage, specific scenarios]
```

### Security Review Delegation

```markdown
@security-reviewer Scan [feature] implementation for vulnerabilities.

Context:
- Project: [type] with [auth method] authentication
- Framework: [framework + language]
- Focus: [specific areas to review]

Files to review:
- [path/to/auth.ts] (authentication logic)
- [path/to/middleware.ts] (middleware)
- [path/to/routes.ts] (routes)

Requirements (from EPCC_PLAN.md):
- [Security requirements]

Check for:
- OWASP Top 10 vulnerabilities
- [Technology]-specific security best practices
- Input validation gaps
- Authentication/authorization issues

Deliverable: Security report with severity levels, specific fixes
```

### Documentation Generation Delegation

```markdown
@documentation-agent Generate API documentation for [feature].

Context:
- Project: [API type]
- Framework: [framework + language]
- Doc style: [OpenAPI/JSDoc/etc. from EPCC_EXPLORE.md]

Files to document:
- [path/to/routes.ts] (endpoints)
- [path/to/middleware.ts] (middleware)

Requirements:
- API endpoint documentation (request/response formats)
- [Feature] flow explanation
- Error code reference
- Usage examples

Deliverable: README section + inline comments + API spec
```

### When to Use Sub-Agents

- **Use for**: Complex test suites, security audits, comprehensive documentation
- **Don't use for**: Simple tests, basic docs, standard implementations (you have full context)

## init.sh Generation

When TECH_REQ.md specifies `init.sh required: Yes`, generate or regenerate the init.sh script.

**Auto-regeneration triggers:**
- init.sh doesn't exist
- TECH_REQ.md is newer than init.sh (TRD was updated)

**Template:**

```bash
#!/bin/bash
# init.sh - Generated from TECH_REQ.md Environment Setup
# Regenerate by updating TECH_REQ.md and running /epcc-code
set -e

PROJECT_NAME="[from TRD]"
echo "Setting up $PROJECT_NAME..."

# Prerequisites check
check_prereqs() {
    echo "Checking prerequisites..."
    command -v [required_command] >/dev/null 2>&1 || { echo "[tool] required"; exit 1; }
}

# Virtual environment / package installation
setup_environment() {
    echo "Setting up environment..."
    # Based on TRD: venv, npm install, etc.
}

# Install dependencies
install_deps() {
    echo "Installing dependencies..."
    # Based on TRD: pip install, npm ci, etc.
}

# Start services
start_services() {
    echo "Starting services..."
    # Based on TRD: database, redis, etc.
}

# Start development server
start_dev_server() {
    echo "Starting development server..."
    # Based on TRD startup command
}

# Health check
verify_ready() {
    echo "Verifying environment..."
    # Based on TRD health check
}

# Run setup
check_prereqs
setup_environment
install_deps
start_services
start_dev_server &
sleep 2
verify_ready

echo "Environment ready!"
```

**Customization notes:**
- Adapt template to actual TRD requirements
- Include only components marked in TRD checklist
- Use startup command and health check from TRD verbatim
- For complex setups, consider docker-compose alternative

## Error Handling Implementation

**Agent-Compatible Pattern** (for sub-agent observability):

```typescript
// Exit code 2 + stderr for recoverable errors
try {
    const result = await operation();
    if (!result.success) {
        console.error(`ERROR: ${result.message}`);
        process.exit(2);  // Recoverable error
    }
} catch (error) {
    console.error(`ERROR: ${error.message}`);
    process.exit(2);
}

// Exit code 1 for unrecoverable errors
if (criticalResourceMissing) {
    console.error("FATAL: Database connection failed");
    process.exit(1);  // Unrecoverable
}
```

**Pattern**: Exit code 2 + stderr = agent can observe and retry.

## EPCC_CODE.md Output Template

```markdown
# Implementation: [Feature Name]

**Mode**: [--tdd/--quick/--full/default] | **Date**: [Date] | **Status**: [Complete/Blocked]

## 1. Changes ([X files], [+Y -Z lines], [A% coverage])
**Created**: [file:line] - [Purpose]
**Modified**: [file:line] - [What changed]

## 2. Quality (Tests [X%] | Security [Clean/Findings] | Docs [Updated/Skipped])
**Tests**: [X unit, Y integration, Z edge cases] - Target met: [Y/N]
**Security**: [Scan results or "Reviewed in security-reviewer output"]
**Docs**: [What was updated - API docs, README, inline comments]

## 3. Decisions
**[Decision name]**: [Choice made] | Why: [Rationale] | Alt: [Options considered]
**[Trade-off]**: Optimized [X] over [Y] because [reason]

## 4. Handoff
**Run**: `/epcc-commit` when ready
**Blockers**: [None / Describe blocking issues]
**TODOs**: [Deferred work or follow-ups]

---

## Context Used

**Planning**: [EPCC_PLAN.md approach] | **Tech**: [TECH_REQ.md insights used]
**Exploration**: [Patterns from EPCC_EXPLORE.md or autonomous /epcc-explore]
**Research**: [WebSearch/WebFetch findings applied, if any]
**Patterns**: [Code patterns/components reused]
```

**Mode adaptation**:
- **--quick mode** (~150-250 tokens): Changes + Quality summary only
- **--full mode** (~400-600 tokens): All 4 dimensions with comprehensive detail
