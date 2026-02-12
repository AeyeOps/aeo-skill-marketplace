# Cross-Cutting Marketplace Analysis
**Date:** 2026-02-12
**Scope:** All 17 plugins in aeo-skill-marketplace
**Analyst:** cross-cutting-analyst

---

## Summary

| Category | Issues Found | HIGH | MEDIUM | LOW |
|----------|-------------|------|--------|-----|
| Agent duplication | 1 (systemic) | 1 | 0 | 0 |
| Command conflicts | 1 | 1 | 0 | 0 |
| Broken references | 1 | 1 | 0 | 0 |
| Invalid tools | 1 | 0 | 1 | 0 |
| Plugin overlaps | 3 | 0 | 3 | 0 |
| Functionality gaps | 1 | 0 | 1 | 0 |
| Model selection | 1 | 0 | 1 | 0 |
| Naming/format | 3 | 0 | 0 | 3 |
| marketplace.json | 2 | 0 | 1 | 1 |
| Best practices | 2 | 0 | 2 | 0 |
| **TOTAL** | **16** | **3** | **9** | **4** |

---

## HIGH Severity

### ISSUE CC-1: Massive Identical Agent Duplication Across Plugins
- **Severity:** HIGH
- **Scope:** 13 agent templates duplicated across 12 plugins, ~50 of 65 total agent files are copies
- **Problem:** The same agent files are copy-pasted byte-for-byte across multiple plugins with zero differentiation. This is not context-specialized reuse; it is wholesale duplication.

| Agent Name | Copies | Plugins |
|------------|--------|---------|
| `test-generator` | 5 | architecture, documentation, epcc-workflow, testing, tdd-workflow |
| `code-archaeologist` | 5 | architecture, code-analysis, documentation, epcc-workflow, troubleshooting |
| `qa-engineer` | 5 | architecture, epcc-workflow, security, testing, tdd-workflow |
| `system-designer` | 6 | architecture, documentation, epcc-workflow, performance, security, testing |
| `business-analyst` | 6 | agile-tools, documentation, epcc-workflow, requirements, security, tdd-workflow |
| `security-reviewer` | 4 | architecture, epcc-workflow, security, tdd-workflow |
| `optimization-engineer` | 3 | documentation, epcc-workflow, performance |
| `tech-evaluator` | 3 | code-analysis, epcc-workflow, requirements |
| `ux-optimizer` | 3 | documentation, epcc-workflow, ux-design |
| `performance-profiler` | 3 | architecture, performance, tdd-workflow |
| `deployment-agent` | 2 | deployment, epcc-workflow |
| `documentation-agent` | 2 | documentation, epcc-workflow |
| `architecture-documenter` | 2 | architecture, documentation |

- **Impact:**
  - Users installing multiple plugins get conflicting agent names (e.g., two identical `test-generator` agents)
  - Maintenance nightmare: a fix to one agent must be applied to 5+ copies
  - Inflates marketplace size (~50 redundant files)
  - `aeo-epcc-workflow` alone contains 12 agents, 10 of which are copies from specialized plugins
- **Fix:** Extract shared agents to a `aeo-core-agents` base plugin. Other plugins should declare dependencies on shared agents rather than bundling copies. If Claude Code doesn't support cross-plugin agent references, document this as a platform limitation and consolidate the canonical copy in the most relevant plugin.

---

### ISSUE CC-2: /prd Command Name Collision
- **Severity:** HIGH
- **Scope:** `aeo-epcc-workflow/commands/prd.md`, `aeo-requirements/commands/prd.md`
- **Problem:** Two different plugins register the `/prd` command with different implementations:
  - **aeo-epcc-workflow**: "Interactive PRD creation - Optional feeder command that prepares requirements before EPCC workflow". Uses a direct interactive approach.
  - **aeo-requirements**: "Product requirements discovery - Create comprehensive PRD through focused questions and guided questionnaire". Uses a hybrid interactive + self-paced questionnaire approach with `--process` flag.
- **Impact:** Users who install both plugins will have a command name collision. Claude Code behavior with duplicate command names is undefined/unpredictable. Users cannot access both implementations.
- **Fix:** Rename one command. Options:
  - Rename aeo-epcc-workflow's to `/epcc-prd` (consistent with its `epcc-` prefix pattern)
  - Rename aeo-requirements' to `/requirements-prd` or `/prd-discovery`

---

### ISSUE CC-3: Broken @reference - EPCC_BEST_PRACTICES.md Missing
- **Severity:** HIGH
- **Scope:** 7 commands in `aeo-epcc-workflow/commands/`: `epcc-explore.md`, `epcc-plan.md`, `epcc-code.md`, `epcc-commit.md`, `epcc-resume.md`, `prd.md`, `trd.md`
- **Problem:** All 7 commands reference `@../docs/EPCC_BEST_PRACTICES.md` but the file `aeo-epcc-workflow/docs/EPCC_BEST_PRACTICES.md` does not exist. The `aeo-epcc-workflow/docs/` directory does not exist at all.
- **Impact:** Every EPCC command fails to load its best practices context. The commands reference this file for critical guidance: clarification strategies, error handling, sub-agent delegation patterns, and workflow optimization. Without it, commands operate with incomplete instructions.
- **Fix:** Create `aeo-epcc-workflow/docs/EPCC_BEST_PRACTICES.md` with the referenced content (clarification decision framework, sub-agent decision matrix, agent capabilities overview, git workflows, quality gates). Alternatively, remove all 7 @references if the content was already inlined in each command.

---

## MEDIUM Severity

### ISSUE CC-4: Invalid/Deprecated Tool Names in Agent Frontmatter
- **Severity:** MEDIUM
- **Scope:** ~25 agent files across 8 plugins
- **Problem:** Multiple agents reference tools that are not part of the current Claude Code tool set:

| Tool Name | Status | Used By | Count |
|-----------|--------|---------|-------|
| `TodoWrite` | Deprecated (replaced by TaskCreate/TaskUpdate) | business-analyst, scrum-master, product-owner, project-manager | 10 agents across 5 plugins |
| `BashOutput` | Not a standard tool (Bash returns output directly) | test-generator, qa-engineer, optimization-engineer, performance-profiler, performance-optimizer, deployment-agent, security-reviewer, troubleshooting qa-engineer | ~20 agents |
| `KillBash` | Not a standard tool (use TaskStop) | deployment-agent | 2 agents |
| `LS` | Not a standard tool (use Bash ls or Glob) | code-archaeologist, system-designer, architecture-documenter, documentation-agent, and others | ~15 agents |

- **Impact:** If Claude Code validates tool names in agent frontmatter, these agents may fail to spawn or run with reduced capabilities. If it ignores unknown tools, the agents still cannot use the intended functionality.
- **Fix:** Replace invalid tool names:
  - `TodoWrite` → `TaskCreate, TaskUpdate, TaskList`
  - `BashOutput` → Remove (Bash returns output natively)
  - `KillBash` → `TaskStop`
  - `LS` → Remove (use `Bash` with `ls` or `Glob`)

---

### ISSUE CC-5: All 65 Agents Use model: opus - No Cost/Latency Optimization
- **Severity:** MEDIUM
- **Scope:** All 65 agent files across all plugins
- **Problem:** Every single agent in the marketplace uses `model: opus`. There is zero model differentiation based on task complexity. Agents performing simple read-only analysis (code-archaeologist, tech-evaluator) use the same expensive model as agents doing complex multi-step reasoning (architect, system-designer).
- **Impact:**
  - Unnecessary cost: opus is the most expensive model tier
  - Unnecessary latency: simpler tasks take longer than needed
  - Poor example for marketplace users: suggests opus is the only valid choice
- **Fix:** Apply model selection based on task complexity:
  - **opus**: Complex reasoning, multi-step planning, architecture design (architect, system-designer, performance-optimizer)
  - **sonnet**: Balanced tasks with code generation (test-generator, qa-engineer, optimization-engineer, deployment-agent)
  - **haiku**: Simple/fast tasks, read-only analysis, formatting (code-archaeologist for initial scans, documentation formatting agents)

---

### ISSUE CC-6: aeo-testing vs aeo-tdd-workflow - Confusing Overlap
- **Severity:** MEDIUM
- **Scope:** `aeo-testing` (3 agents, 1 command, 1 skill), `aeo-tdd-workflow` (6 agents, 2 commands, 0 skills)
- **Problem:** These plugins have overlapping scope with unclear differentiation:
  - Both contain identical copies of `test-generator` and `qa-engineer`
  - `test-generator` in aeo-testing has a TDD-focused description ("Writes failing tests FIRST, Red phase of TDD") - identical to aeo-tdd-workflow's copy
  - aeo-testing's `/generate-tests` delegates to `@test-generator @qa-engineer @system-designer`
  - aeo-tdd-workflow's `/tdd-feature` and `/tdd-bugfix` also use the same agents
  - The marketplace descriptions differentiate them as "Quality assurance agents for test planning" vs "Test-driven development agents enforcing red-green-refactor" but the underlying agents are identical
- **Impact:** Users cannot determine which plugin to install. Installing both gives duplicate agents with the same names.
- **Fix:** Either:
  1. **Merge** into a single `aeo-testing` plugin with TDD commands as an optional workflow
  2. **Differentiate**: Make aeo-testing focus on post-hoc test generation/QA and aeo-tdd-workflow focus strictly on TDD methodology. Give them unique agent copies with specialized descriptions.

---

### ISSUE CC-7: aeo-code-analysis is Redundant with aeo-architecture
- **Severity:** MEDIUM
- **Scope:** `aeo-code-analysis` (2 agents, 0 commands, 0 skills), `aeo-architecture` (10 agents, 3 commands, 1 skill)
- **Problem:** aeo-code-analysis contains only 2 agents: `code-archaeologist` and `tech-evaluator`. Both are identical copies of agents already in aeo-architecture (and aeo-epcc-workflow). aeo-code-analysis has NO commands, NO skills - it provides zero unique value.
- **Impact:** Confusing for users. aeo-code-analysis appears as a distinct plugin in the marketplace but adds nothing that isn't already in aeo-architecture. The `/code-review` command in aeo-architecture already covers code analysis use cases.
- **Fix:** Either:
  1. **Remove** aeo-code-analysis entirely and ensure aeo-architecture covers all code analysis use cases
  2. **Enhance** aeo-code-analysis with unique commands (e.g., `/analyze-codebase`, `/tech-debt-report`) and unique agents that differentiate it from aeo-architecture

---

### ISSUE CC-8: aeo-epcc-workflow is a "Kitchen Sink" Super-Plugin
- **Severity:** MEDIUM
- **Scope:** `aeo-epcc-workflow` (12 agents, 7 commands, 0 skills)
- **Problem:** aeo-epcc-workflow contains 12 agents - the most of any plugin. 10 of these 12 are identical copies from specialized plugins:
  - code-archaeologist (from aeo-code-analysis)
  - business-analyst (from aeo-agile-tools, aeo-requirements)
  - project-manager (from aeo-agile-tools)
  - system-designer (from aeo-architecture)
  - tech-evaluator (from aeo-code-analysis, aeo-requirements)
  - security-reviewer (from aeo-security)
  - documentation-agent (from aeo-documentation)
  - optimization-engineer (from aeo-performance)
  - qa-engineer (from aeo-testing)
  - test-generator (from aeo-testing)
  - ux-optimizer (from aeo-ux-design)
  - deployment-agent (from aeo-deployment)

  Only 0 agents are unique to aeo-epcc-workflow - all 12 are copies.
- **Impact:** Installing aeo-epcc-workflow effectively replaces 8 specialized plugins, making the marketplace's modular design pointless. Users choosing specialized plugins alongside EPCC get agent name conflicts.
- **Fix:** EPCC commands should reference agents from specialized plugins (via cross-plugin dependencies) rather than bundling copies. The `@agent-name` references in commands already support this pattern - the agent files don't need to be local.

---

### ISSUE CC-9: Functionality Gaps - Missing Common Development Workflows
- **Severity:** MEDIUM
- **Scope:** Entire marketplace
- **Problem:** Several common development workflows have no plugin coverage:

| Missing Area | Description | Closest Existing |
|-------------|-------------|-----------------|
| CI/CD Pipeline Design | GitHub Actions, GitLab CI, Jenkins pipeline creation and debugging | aeo-deployment (deployment only, not CI/CD authoring) |
| Database Design & Migration | Schema design, migration scripts, ORM patterns | None |
| API Design (OpenAPI/REST) | OpenAPI spec authoring, REST best practices, API versioning | None |
| Containerization | Dockerfile authoring, Docker Compose, Kubernetes manifests | None |
| Infrastructure as Code | Terraform, Pulumi, CloudFormation | None |
| Dependency Management | Version conflicts, security advisories, upgrade strategies | None |
| Git Workflow | Branch strategies, merge conflict resolution, rebase workflows | aeo-epcc-workflow has /epcc-commit but no general git tooling |

- **Impact:** Users must look outside the marketplace for common workflows. The marketplace is heavily weighted toward analysis/documentation/testing with gaps in build/deploy/infrastructure.
- **Fix:** Prioritize new plugins for the highest-demand gaps: CI/CD, API Design, and Database Design would add the most value.

---

### ISSUE CC-10: Agent Descriptions Not Optimized for Triggering
- **Severity:** MEDIUM
- **Scope:** All 65 agents across all plugins
- **Problem:** Claude Code agent descriptions serve as triggering conditions - they determine when an agent is automatically suggested. Best practice is "Use this agent when..." phrasing. Current agents use inconsistent patterns:
  - "Deploy when working with..." (code-archaeologist)
  - "Activate to enforce..." (test-generator)
  - "Invoke before releases..." (qa-engineer)
  - "Run before deployments..." (security-reviewer)
  - "Engage for major system..." (architect)
  - "Use for orchestrating..." (deployment-agent) - closest to best practice

  None use the recommended "Use this agent when..." pattern consistently.
- **Impact:** Reduced agent discoverability. Claude Code's agent matching may be less effective with passive/varied description patterns compared to explicit "Use this agent when..." trigger phrases.
- **Fix:** Standardize all agent descriptions to start with "Use this agent when..." followed by specific trigger scenarios. Example: `"Use this agent when working with legacy or undocumented systems..."` instead of `"Deploy when working with legacy..."`.

---

### ISSUE CC-11: Hollow Plugins - Agents Only, No Commands or Skills
- **Severity:** MEDIUM
- **Scope:** 5 plugins
- **Problem:** Several plugins contain only agents with no commands or skills, making them agent-only containers with limited interactive value:

| Plugin | Agents | Commands | Skills | Assessment |
|--------|--------|----------|--------|------------|
| aeo-agile-tools | 4 | 0 | 0 | No entry points for users |
| aeo-code-analysis | 2 | 0 | 0 | Redundant (see CC-7) |
| aeo-deployment | 1 | 0 | 0 | Single agent, no workflows |
| aeo-troubleshooting | 2 | 1 | 0 | Has /troubleshoot but no skills |
| aeo-security | 4 | 2 | 0 | Has commands but no domain knowledge skills |

- **Impact:** Agents without commands or skills are harder to discover and use. Users typically interact through commands (`/command`) or benefit from contextual skills. Agent-only plugins require users to know agent names or rely on auto-triggering.
- **Fix:** Add at least one command per plugin as a user entry point:
  - aeo-agile-tools: `/sprint-plan`, `/backlog-groom`
  - aeo-deployment: `/deploy`, `/rollback`
  - aeo-security: already has `/security-scan`, add a skill for security best practices

---

## LOW Severity

### ISSUE CC-12: Tools Field Format Inconsistency
- **Severity:** LOW
- **Scope:** All 65 agent files
- **Problem:** Agent frontmatter uses two different formats for the `tools` field:
  - Array syntax: `tools: [Read, Write, Edit, MultiEdit, Grep, Glob, Bash, BashOutput]` (~30 agents)
  - Comma-separated: `tools: Read, Write, Edit, MultiEdit, Grep, Glob, Bash, BashOutput` (~35 agents)

  Both formats may be parsed correctly, but the inconsistency is unprofessional.
- **Impact:** Minor. May cause parsing issues if the YAML parser is strict about array vs string.
- **Fix:** Standardize on one format. Recommend YAML array syntax `tools: [Read, Write, Edit]` as it's unambiguous.

---

### ISSUE CC-13: All Plugins at Version 0.1.0
- **Severity:** LOW
- **Scope:** All 17 plugin.json manifests
- **Problem:** Every plugin is at version `0.1.0`. No version differentiation despite varying maturity levels. aeo-claude and aeo-n8n have extensive, polished content (10 skills, reference docs) while aeo-code-analysis has only 2 copied agents, yet both claim the same version.
- **Impact:** Users cannot gauge plugin maturity from version numbers. No versioning progression visible.
- **Fix:** Version plugins based on actual maturity:
  - Well-developed plugins (aeo-claude, aeo-epcc-workflow, aeo-n8n, aeo-python, aeo-documentation): bump to 0.2.0+
  - Minimal plugins (aeo-code-analysis, aeo-deployment): keep at 0.1.0
  - Establish a versioning policy: 0.1.x = initial, 0.2.x = commands+skills, 1.0.x = production-ready

---

### ISSUE CC-14: Skill Name Inconsistency in Frontmatter
- **Severity:** LOW
- **Scope:** `aeo-claude/skills/claude-agent-sdk/SKILL.md`
- **Problem:** The claude-agent-sdk skill uses `name: Claude Agent SDK Reference` (Title Case with spaces) while all other skills use kebab-case names (e.g., `name: mcp-architect-designer`, `name: ultrareview-loop`, `name: n8n-code-javascript`).
- **Impact:** Minor naming inconsistency. May affect skill lookup if Claude Code normalizes names to kebab-case.
- **Fix:** Rename to `name: claude-agent-sdk` to match the directory name and other skill naming conventions.

---

### ISSUE CC-15: marketplace.json Category Assignments
- **Severity:** LOW
- **Scope:** `.claude-plugin/marketplace.json`
- **Problem:** Category assignments are inconsistent:
  - `aeo-performance` is categorized as `development` but should be `development` or a dedicated `performance` category
  - `aeo-troubleshooting` is `development` but could be `devops` or `debugging`
  - `aeo-agile-tools` and `aeo-requirements` are both `productivity` - these are more `project-management` or `planning`
  - 8 of 17 plugins are `development` - the category is too broad
  - Missing a `workflow` category for aeo-epcc-workflow (currently `development`)
- **Impact:** Users filtering by category get unhelpful results. "development" matches half the marketplace.
- **Fix:** Introduce more specific categories: `workflow`, `project-management`, `devops`, `analysis`. Redistribute plugins accordingly.

---

### ISSUE CC-16: marketplace.json Tag Gaps
- **Severity:** MEDIUM
- **Scope:** `.claude-plugin/marketplace.json`
- **Problem:** Several plugins have missing or insufficient tags:
  - `aeo-troubleshooting`: tags `["debugging", "troubleshooting", "problem-solving"]` - missing `"root-cause-analysis"`, `"incident-response"`
  - `aeo-documentation`: tags `["documentation", "diataxis", "technical-writing"]` - missing `"mermaid"`, `"diagrams"` (has a mermaid skill)
  - `aeo-epcc-workflow`: tags `["workflow", "epcc", "development-process"]` - missing `"explore"`, `"plan"`, `"commit"` (its core phases)
  - `aeo-claude`: tags `["claude", "agent-sdk", "skills", "prompting", "slash-commands"]` - missing `"ultrareview"`, `"validation"`, `"teams"` (major features)
  - `aeo-python`: missing `"data-engineering"` tag despite having a data engineering skill... wait it has it. But missing `"uv"`, `"typer"`, `"click"` (covered technologies)
  - `aeo-architecture`: missing `"mcp"`, `"code-review"` tags (has MCP skill and code-review command)
- **Impact:** Users searching by tag may miss relevant plugins.
- **Fix:** Audit and expand tags for each plugin to cover all major features and commands.

---

## Cross-Reference Validation Summary

| Reference Pattern | Status | Details |
|-------------------|--------|---------|
| `@../docs/EPCC_BEST_PRACTICES.md` | BROKEN | Referenced by 7 EPCC commands, file does not exist (CC-3) |
| `@agent-name` in commands | VALID | Agent references in commands work via agent auto-discovery |
| `[references/file.md]()` in skills | VALID | All checked reference files exist in their skill directories |
| `${CLAUDE_PLUGIN_ROOT}/...` in hooks | VALID | Checked loop-hook.sh - exists |
| `$CLAUDE_PROJECT_DIR/hooks/...` in hooks | BY DESIGN | Project-level scripts expected to be user-provided |

---

## Plugin Completeness Matrix

| Plugin | Agents | Commands | Skills | Hooks | Unique Content |
|--------|--------|----------|--------|-------|---------------|
| aeo-agile-tools | 4 | 0 | 0 | Y | project-manager, product-owner, scrum-master (unique to this plugin) |
| aeo-architecture | 10 | 3 | 1 | Y | architect, simple-architect, simple-architecture-documenter (unique) |
| aeo-claude | 0 | 0 | 10 | Y | All skills unique - major value plugin |
| aeo-code-analysis | 2 | 0 | 0 | N | NO unique content (all copies) |
| aeo-deployment | 1 | 0 | 0 | Y | NO unique agents (deployment-agent also in epcc) |
| aeo-documentation | 12 | 5 | 1 | N | docs-tutorial/howto/explanation/reference agents (unique) |
| aeo-epcc-workflow | 12 | 7 | 0 | Y | 7 commands unique, 0 agents unique |
| aeo-n8n | 0 | 0 | 7 | N | All skills unique - domain knowledge plugin |
| aeo-nous | 0 | 1 | 1 | Y | All unique - self-improving context system |
| aeo-performance | 5 | 1 | 0 | Y | performance-optimizer (unique) |
| aeo-python | 0 | 0 | 3 | N | All skills unique - language-specific plugin |
| aeo-requirements | 2 | 2 | 0 | N | /prd (different impl), /tech-req unique |
| aeo-security | 4 | 2 | 0 | Y | /security-scan, /permission-audit unique |
| aeo-tdd-workflow | 6 | 2 | 0 | N | /tdd-feature, /tdd-bugfix unique |
| aeo-testing | 3 | 1 | 1 | Y | automating-computer-use-testing skill (unique) |
| aeo-troubleshooting | 2 | 1 | 0 | N | /troubleshoot command unique |
| aeo-ux-design | 2 | 0 | 1 | N | ui-designer, react-pwa-designer skill (unique) |

---

## Recommendations Priority

1. **Immediately** (CC-3): Create or remove EPCC_BEST_PRACTICES.md - 7 commands are broken
2. **Immediately** (CC-2): Rename one of the `/prd` commands to resolve collision
3. **Short-term** (CC-1): Design a shared agent strategy to eliminate 50+ duplicate files
4. **Short-term** (CC-4): Fix invalid tool names in agent frontmatter
5. **Short-term** (CC-7): Merge or differentiate aeo-code-analysis
6. **Medium-term** (CC-5, CC-10): Optimize model selection and agent descriptions
7. **Medium-term** (CC-6, CC-8): Reduce plugin overlap between testing/tdd and epcc/others
8. **Long-term** (CC-9): Build plugins for top functionality gaps (CI/CD, API design, databases)
