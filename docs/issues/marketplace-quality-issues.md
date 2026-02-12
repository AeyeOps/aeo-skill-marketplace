# AEO Skill Marketplace — Quality Issues

**Date:** 2026-02-12
**Scope:** All 16 plugins (was 17), 25 agents (was 65), 30 commands, 17 skills, 11 hooks files
**Prior audit:** [aeo-marketplace-audit.md](aeo-marketplace-audit.md) (spec compliance — mostly resolved)
**Source reports:** [group-a-findings.md](group-a-findings.md), [group-b-findings.md](group-b-findings.md), [cross-cutting-findings.md](cross-cutting-findings.md)

---

## Summary

| # | Issue | Severity | Category | Plugins Affected | Status |
|---|-------|----------|----------|------------------|--------|
| 1 | Massive agent duplication (~50 of 65 files are copies) | HIGH | Architecture | 12 plugins | FIXED (v0.3.0) |
| 2 | Invalid/non-existent tool names in agent frontmatter | HIGH | Agent Quality | 13 plugins, ~45 agents | FIXED (e17d2b6 + v0.3.0) |
| 3 | Broken @reference — EPCC_BEST_PRACTICES.md missing | HIGH | Broken Reference | aeo-epcc-workflow (7 commands) | FIXED (e17d2b6) |
| 4 | `/prd` command name collision | HIGH | Command Conflict | aeo-epcc-workflow, aeo-requirements | FIXED (e17d2b6) |
| 5 | Unfilled template placeholders in agent prompts | HIGH | Agent Quality | 6+ plugins, 18+ agents | FIXED (e17d2b6) |
| 6 | aeo-performance hooks reference non-existent scripts | HIGH | Hooks | aeo-performance | FIXED (e17d2b6) |
| 7 | aeo-performance hooks have shell variable expansion bugs | HIGH | Hooks | aeo-performance | FIXED (e17d2b6) |
| 8 | aeo-testing hooks.json empty with orphaned scripts | HIGH | Hooks | aeo-testing | FIXED (v0.3.0) |
| 9 | aeo-nous version mismatch (plugin.json 0.3.0 vs setup.md 0.4.0) | HIGH | Metadata | aeo-nous | FIXED (v0.4.0) |
| 10 | All 65 agents use `model: opus` — zero cost optimization | MEDIUM | Agent Quality | All plugins | FIXED (v0.3.0) |
| 11 | Agent descriptions not optimized for triggering | MEDIUM | Agent Quality | All plugins | FIXED (v0.3.0) |
| 12 | aeo-testing vs aeo-tdd-workflow confusing overlap | MEDIUM | Architecture | aeo-testing, aeo-tdd-workflow | MOSTLY RESOLVED |
| 13 | aeo-code-analysis is redundant (zero unique content) | MEDIUM | Architecture | aeo-code-analysis | FIXED (v0.3.0) |
| 14 | aeo-epcc-workflow is a "kitchen sink" super-plugin | MEDIUM | Architecture | aeo-epcc-workflow | FIXED (v0.3.0) |
| 15 | EPCC commands are 630–1378 lines each | MEDIUM | Command Quality | aeo-epcc-workflow | FIXED (v0.4.0) |
| 16 | 2 hollow plugins — agents only, no commands or skills | MEDIUM | Completeness | aeo-agile-tools, aeo-deployment | FIXED (v0.4.0) |
| 17 | 5 plugins have zero skills (knowledge-light) | MEDIUM | Completeness | 5 plugins | FIXED (v0.4.0) |
| 18 | Functionality gaps — no CI/CD, DB, API, container plugins | MEDIUM | Marketplace Gaps | Entire marketplace | OPEN |
| 19 | Skills use markdown links instead of @reference syntax | MEDIUM | Skill Quality | aeo-python, aeo-testing, aeo-ux-design | FIXED (v0.4.0) |
| 20 | aeo-ux-design scope mismatch (claims accessibility) | MEDIUM | Metadata | aeo-ux-design | INVALID — accessibility content exists |
| 21 | Redundant architect variants without differentiation | MEDIUM | Agent Quality | aeo-architecture | FIXED (v0.3.0) |
| 22 | aeo-python has no agents, commands, or hooks | MEDIUM | Completeness | aeo-python | CLOSED (intentional design) |
| 23 | marketplace.json tag gaps | MEDIUM | Metadata | 6 plugins | FIXED (v0.4.0) |
| 24 | Disabled hooks with misleading descriptions | MEDIUM | Hooks | aeo-agile-tools, aeo-deployment | FIXED (pre-v0.3.0) |
| 25 | aeo-performance echo-to-stderr hooks add noise | MEDIUM | Hooks | aeo-performance | FIXED (e17d2b6) |
| 26 | aeo-security hooks use wrong path variable | LOW | Hooks | aeo-security | FIXED (e17d2b6) |
| 27 | Agent changelog versions don't match frontmatter | LOW | Metadata | 6+ plugins | FIXED (v0.4.0) |
| 28 | Tools field format inconsistency (array vs comma) | LOW | Consistency | All plugins | FIXED (v0.3.0) |
| 29 | 13 of 16 plugins at version 0.1.0 | LOW | Metadata | 13 plugins | OPEN (3 evolved) |
| 30 | Skill name inconsistency (Title Case vs kebab-case) | LOW | Consistency | aeo-claude | INVALID — all kebab-case |
| 31 | marketplace.json category assignments too broad | LOW | Metadata | marketplace.json | INVALID — distribution reasonable |
| 32 | Inconsistent reference directory naming | LOW | Consistency | aeo-python | INVALID — no inconsistency found |
| 33 | aeo-python skill declares unsupported frontmatter field | LOW | Skill Quality | aeo-python | FIXED (v0.4.0) |
| 34 | aeo-ux-design react-pwa-designer skill too long (676 lines) | MEDIUM | Skill Quality | aeo-ux-design | FIXED (v0.4.0) |
| 35 | aeo-requirements commands use nested markdown fences | LOW | Command Quality | aeo-requirements | FIXED (v0.4.0) |

**Totals: 12 HIGH, 16 MEDIUM, 7 LOW — 27 FIXED, 1 MOSTLY RESOLVED, 4 INVALID, 1 CLOSED, 2 OPEN**

> **Note (v0.3.0):** Agent deduplication reduced 65 agents to 25 unique agents across 16 plugins (down from 17). Six plugins now have cross-plugin companion requirements documented in plugin.json, as their commands reference agents hosted in other plugins via `@agent-name`. Issue 9 remains PARTIAL — plugin.json is 0.3.0 but setup.md references 0.4.0.
>
> **Note (freshness audit):** Issues 20, 30, 31, 32 invalidated on re-inspection — original findings were inaccurate or already resolved before tracking began. Issue 12 mostly resolved by dedup (distinct boundaries now). Issue 16 reduced from 5 to 2 hollow plugins. Issue 21 resolved by description standardization. Issue 24 already fixed (descriptions say "disabled by default").
>
> **Note (v0.4.0):** Round 3 resolved 11 issues: quick fixes (9, 23, 27, 33, 35), @reference syntax and skill restructuring (19, 34), EPCC command extraction (15), new commands and skills (16, 17). Issue 22 closed as intentional design (skills-only is valid). Remaining open: 18 (new plugins, deferred), 29 (version progression, cosmetic).

---

## HIGH Severity Issues

### ISSUE 1: Massive Agent Duplication (~50 of 65 files are copies)
- **Plugins:** 12 of 17 plugins affected
- **Problem:** 13 agent templates are copy-pasted identically across plugins. ~50 of 65 agent files are byte-for-byte duplicates. `aeo-epcc-workflow` has 12 agents — ALL copied from other plugins (zero unique agents). `aeo-documentation` has 7/12 duplicates. `aeo-code-analysis` has 2/2 duplicates.

  | Agent Name | Copies | Source Plugins |
  |------------|--------|----------------|
  | system-designer | 6 | architecture, documentation, epcc-workflow, performance, security, testing |
  | business-analyst | 6 | agile-tools, documentation, epcc-workflow, requirements, security, tdd-workflow |
  | code-archaeologist | 5 | architecture, code-analysis, documentation, epcc-workflow, troubleshooting |
  | test-generator | 5 | architecture, documentation, epcc-workflow, testing, tdd-workflow |
  | qa-engineer | 5 | architecture, epcc-workflow, security, testing, tdd-workflow |
  | security-reviewer | 4 | architecture, epcc-workflow, security, tdd-workflow |
  | optimization-engineer | 3 | documentation, epcc-workflow, performance |
  | tech-evaluator | 3 | code-analysis, epcc-workflow, requirements |
  | ux-optimizer | 3 | documentation, epcc-workflow, ux-design |
  | performance-profiler | 3 | architecture, performance, tdd-workflow |
  | deployment-agent | 2 | deployment, epcc-workflow |
  | documentation-agent | 2 | documentation, epcc-workflow |
  | architecture-documenter | 2 | architecture, documentation |

- **Impact:** Name collisions when multiple plugins loaded (undefined behavior). Maintenance nightmare — fixing one agent requires updating 5+ copies. Inflates marketplace size. Makes modular plugin design pointless.
- **Fix:** Extract shared agents to an `aeo-core-agents` base plugin. Other plugins declare dependencies. If Claude Code doesn't support cross-plugin agent references, keep canonical copies in the most relevant plugin and remove all duplicates. EPCC commands already use `@agent-name` references which work via auto-discovery — the agent files don't need to be colocated.

---

### ISSUE 2: Invalid/Non-Existent Tool Names in Agent Frontmatter
- **Plugins:** 13 plugins, ~45 agent files
- **Problem:** Agents declare tools that don't exist in Claude Code:

  | Invalid Tool | Occurrences | Replacement |
  |-------------|-------------|-------------|
  | `MultiEdit` | ~25 agents | `Edit` |
  | `LS` | ~15 agents | `Glob` (or `Bash` with `ls`) |
  | `BashOutput` | ~20 agents | Remove — `Bash` returns output natively |
  | `TodoWrite` | ~10 agents | Remove, or `TaskCreate`/`TaskUpdate` |
  | `KillBash` | 2 agents | Remove, or `TaskStop` |

  Root cause: likely the CLAUDE.md example at line 33 showing `LS` as a valid tool in agent frontmatter.
- **Impact:** Agents silently lack intended capabilities. Claude Code ignores invalid tool names — agents can't edit files (MultiEdit), list directories (LS), or manage tasks (TodoWrite) as their prompts intend.
- **Fix:** Global find-and-replace across all agent files. Also fix the CLAUDE.md agent frontmatter example to only list valid tools: `Read, Write, Edit, Grep, Glob, Bash, WebSearch, WebFetch, Task, TaskCreate, TaskUpdate, TaskList, TaskGet, TaskStop, Skill, NotebookEdit`.

---

### ISSUE 3: Broken @reference — EPCC_BEST_PRACTICES.md Missing
- **Plugin:** aeo-epcc-workflow
- **Files:** All 7 commands: `epcc-explore.md`, `epcc-plan.md`, `epcc-code.md`, `epcc-commit.md`, `epcc-resume.md`, `prd.md`, `trd.md`
- **Problem:** All 7 commands reference `@../docs/EPCC_BEST_PRACTICES.md` but the file does not exist. The `docs/` directory doesn't exist at all in the plugin.
- **Impact:** Every EPCC command fails to load its best practices context (clarification strategies, error handling, sub-agent delegation patterns, workflow optimization).
- **Fix:** Create `aeo-epcc-workflow/docs/EPCC_BEST_PRACTICES.md` with the referenced content, or remove the @references if content was inlined.

---

### ISSUE 4: `/prd` Command Name Collision
- **Plugin:** aeo-epcc-workflow, aeo-requirements
- **Files:** `aeo-epcc-workflow/commands/prd.md`, `aeo-requirements/commands/prd.md`
- **Problem:** Two plugins register `/prd` with different implementations. EPCC version is an interactive PRD creator. Requirements version uses a guided questionnaire with `--process` flag.
- **Impact:** Users installing both plugins get undefined behavior — which `/prd` fires is unpredictable.
- **Fix:** Rename EPCC's to `/epcc-prd` (consistent with its `epcc-` prefix pattern).

---

### ISSUE 5: Unfilled Template Placeholders in Agent Prompts
- **Plugins:** aeo-performance, aeo-requirements, aeo-security, aeo-tdd-workflow, aeo-testing, aeo-troubleshooting
- **Files:** 18+ agent .md files
- **Problem:** Agent system prompts contain unfilled template markers that were never completed:
  ```
  ### Input Requirements
  - [Required inputs]
  ### Output Contract
  - [Expected outputs]
  ### Compatible Agents
  - **Upstream**: [agents that feed into this]
  - **Downstream**: [agents this feeds into]
  ## Edge Cases & Failure Modes
  ### When [Common Edge Case]
  - **Behavior**: [What agent does]
  ```
- **Impact:** Wastes context tokens. Signals incomplete development to the agent. Template artifacts degrade perceived quality.
- **Fix:** Either fill in with actual details or remove the placeholder sections entirely.

---

### ISSUE 6: aeo-performance Hooks Reference Non-Existent Scripts
- **Plugin:** aeo-performance
- **File:** `hooks/hooks.json`
- **Problem:** Stop and SubagentStop hooks reference 4 Python scripts that don't exist:
  - `scripts/calculate_agent_cost.py`
  - `scripts/generate_performance_report.py`
  - `scripts/calculate_session_cost.py`
  - `scripts/identify_bottlenecks.py`
- **Impact:** Hooks fail at runtime, potentially blocking Stop events.
- **Fix:** Create the scripts, or remove the broken hook entries.

---

### ISSUE 7: aeo-performance Hooks Have Shell Variable Expansion Bugs
- **Plugin:** aeo-performance
- **File:** `hooks/hooks.json`
- **Problem:** Hook commands use `${file_path}`, `${query}`, `${agent_name}`, `${duration}`, `${model}` variables that aren't in hook context. Additionally, `${file_path}` inside single-quoted awk strings won't expand:
  ```json
  "command": "wc -l ${file_path} | awk '{print \"FILE_SIZE,${file_path},\"$1}'"
  ```
- **Impact:** Hooks log empty/literal variable names instead of values.
- **Fix:** Verify which variables Claude Code provides to hooks. Fix quoting. Hook data comes via stdin JSON, not environment variables — use `jq` to extract fields.

---

### ISSUE 8: aeo-testing hooks.json Empty with Orphaned Scripts
- **Plugin:** aeo-testing
- **Files:** `hooks/hooks.json`, `hooks/black_formatter.py`, `hooks/python_lint.py`, `hooks/use_uv.py`, `hooks/ruff.toml`
- **Problem:** `hooks.json` has `"hooks": {}` (empty) but the directory contains 4 useful Python scripts (black formatting, ruff linting, uv enforcement) that are never referenced.
- **Impact:** Quality gate scripts are present but inactive and undiscoverable.
- **Fix:** Wire the scripts into hooks.json with appropriate events, or document them in a README with instructions for enabling.

---

### ISSUE 9: aeo-nous Version Mismatch
- **Plugin:** aeo-nous
- **Files:** `.claude-plugin/plugin.json` (0.1.5), `commands/setup.md` (0.3.0)
- **Problem:** Plugin manifest says 0.1.5, setup command says 0.3.0.
- **Impact:** Users and tooling can't determine actual plugin version.
- **Fix:** Synchronize to a single version across all components.

---

## MEDIUM Severity Issues

### ISSUE 10: All 65 Agents Use `model: opus` — Zero Cost Optimization
- **Scope:** All plugins with agents
- **Problem:** Every agent uses `model: opus` regardless of task complexity. Simple read-only analysis (code-archaeologist) uses the same model as complex multi-step architecture design.
- **Impact:** Unnecessary cost and latency for simpler tasks. Poor example for marketplace users.
- **Fix:** Apply tiered model selection:
  - **opus**: Complex reasoning (architect, system-designer, performance-optimizer)
  - **sonnet**: Code generation, testing, documentation (test-generator, qa-engineer, documentation-agent)
  - **haiku**: Simple retrieval, formatting, scanning (code-archaeologist initial pass)

### ISSUE 11: Agent Descriptions Not Optimized for Triggering
- **Scope:** All 65 agents
- **Problem:** Descriptions use inconsistent verb patterns ("Deploy when...", "Activate to...", "Invoke before...") instead of the recommended "Use this agent when..." pattern with specific trigger examples.
- **Impact:** Reduced agent discoverability and matching accuracy.
- **Fix:** Standardize: `"Use this agent when [specific scenario]. Examples: '[user phrase 1]', '[user phrase 2]'"`

### ISSUE 12: aeo-testing vs aeo-tdd-workflow Confusing Overlap
- **Scope:** aeo-testing, aeo-tdd-workflow
- **Problem:** Both contain identical copies of `test-generator` and `qa-engineer`. Both claim TDD focus. Marketplace descriptions attempt differentiation ("quality assurance" vs "red-green-refactor") but underlying agents are identical.
- **Impact:** Users can't determine which to install. Installing both causes agent name conflicts.
- **Fix:** Merge into a single testing plugin with TDD commands as an optional workflow, OR sharply differentiate (testing = post-hoc QA, tdd = strict red-green-refactor with enforcement hooks).

### ISSUE 13: aeo-code-analysis is Redundant
- **Scope:** aeo-code-analysis
- **Problem:** Contains only 2 agents (code-archaeologist, tech-evaluator), both identical copies from aeo-architecture. Zero commands, zero skills, zero unique content.
- **Impact:** Plugin exists as a duplicate container.
- **Fix:** Remove entirely and ensure aeo-architecture covers code analysis, OR add unique commands (`/analyze-codebase`, `/tech-debt-report`) and skills that justify its existence.

### ISSUE 14: aeo-epcc-workflow is a "Kitchen Sink" Super-Plugin
- **Scope:** aeo-epcc-workflow
- **Problem:** 12 agents (all copies), 7 commands (unique), 0 skills. Installing EPCC effectively replaces 8 specialized plugins. The 7 commands are the only unique value — agents add nothing.
- **Impact:** Undermines modular plugin design.
- **Fix:** Remove all duplicate agents from EPCC. Commands already reference agents via `@agent-name` which resolves across installed plugins. Document that EPCC requires relevant specialized plugins to be installed.

### ISSUE 15: EPCC Commands Are 630–1378 Lines Each
- **Scope:** aeo-epcc-workflow
- **Files:** `trd.md` (1378 lines), `prd.md` (824 lines), `epcc-explore.md` (785 lines), `epcc-code.md` (794 lines), `epcc-plan.md` (630 lines), `epcc-commit.md` (631 lines), `epcc-resume.md` (631 lines)
- **Problem:** Every command is 630+ lines. Entire prompt injected into context on invocation.
- **Impact:** Massive context consumption per invocation. Degrades response quality through instruction overload.
- **Fix:** Refactor to ~200 lines per command with `@reference` progressive disclosure for detailed sub-sections.

### ISSUE 16: 5 "Hollow" Plugins — Agents Only
- **Scope:** aeo-agile-tools, aeo-code-analysis, aeo-deployment, aeo-troubleshooting, aeo-security (partial)
- **Problem:** These plugins have agents but no commands or skills (or very few). No user-facing entry points beyond agent auto-triggering.
- **Fix:** Add at least one command per plugin as a user entry point.

### ISSUE 17: 5 Plugins Have Zero Skills
- **Scope:** aeo-requirements, aeo-tdd-workflow, aeo-troubleshooting, aeo-security, aeo-performance
- **Problem:** No contextual domain knowledge. Agents operate solely from their system prompts.
- **Fix:** Add 1-2 skills per plugin covering core domain knowledge that agents can reference.

### ISSUE 18: Functionality Gaps in Marketplace
- **Scope:** Entire marketplace
- **Problem:** Missing coverage for common workflows:

  | Gap | Description |
  |-----|-------------|
  | CI/CD Pipeline Design | GitHub Actions, GitLab CI authoring |
  | Database Design & Migration | Schema design, ORMs, migrations |
  | API Design (OpenAPI/REST) | Spec authoring, versioning, best practices |
  | Containerization | Dockerfile, Docker Compose, Kubernetes |
  | Infrastructure as Code | Terraform, Pulumi, CloudFormation |
  | Dependency Management | Version conflicts, upgrade strategies |
  | Git Workflow | Branch strategies, merge conflict resolution |

- **Fix:** Prioritize CI/CD, API Design, and Database Design as new plugins.

### ISSUE 19: Skills Use Markdown Links Instead of @reference Syntax
- **Scope:** aeo-python, aeo-testing, aeo-ux-design
- **Problem:** `[text](path/to/file.md)` instead of `@relative/path.md`. Referenced content not auto-loaded into context.
- **Fix:** Replace markdown links to reference files with `@relative/path.md`.

### ISSUE 20: aeo-ux-design Scope Mismatch
- **Scope:** aeo-ux-design
- **Problem:** Description claims "accessibility validation and WCAG compliance verification" but only has a React PWA skill. No accessibility tooling.
- **Fix:** Add accessibility/WCAG skill, or revise description to match actual scope.

### ISSUE 21: Redundant Architect Variants in aeo-architecture
- **Scope:** aeo-architecture
- **Problem:** 5 agents overlap: architect, simple-architect, system-designer, architecture-documenter, simple-architecture-documenter. Trigger descriptions don't differentiate clearly.
- **Fix:** Consolidate to 2-3 agents with distinct purposes (design, documentation, review).

### ISSUE 22: aeo-python Has No Agents, Commands, or Hooks
- **Scope:** aeo-python
- **Problem:** Purely passive skills-only plugin. High-quality content but no interactive entry points.
- **Fix:** Add a `/python-init` command or a python-expert agent. Low priority — skills-only is a valid design.

### ISSUE 23: marketplace.json Tag Gaps
- **Scope:** 6 plugins in marketplace.json
- **Problem:** Tags don't cover all major features. E.g., aeo-architecture missing `mcp`, `code-review`; aeo-claude missing `ultrareview`, `teams`.
- **Fix:** Audit and expand tags for each plugin.

### ISSUE 24: Disabled Hooks with Misleading Descriptions
- **Scope:** aeo-agile-tools, aeo-deployment
- **Problem:** hooks.json has `"hooks": {}` but description implies active functionality. aeo-deployment references a README.md that doesn't exist.
- **Fix:** Update descriptions to indicate disabled state, or create the referenced README.

### ISSUE 25: aeo-performance Echo-to-stderr Hooks
- **Scope:** aeo-performance
- **Problem:** PreToolUse/PostToolUse hooks emit "Read operation started", "Command started" to stderr with no actionable value.
- **Fix:** Remove or redirect to a log file.

### ISSUE 34: aeo-ux-design Skill Too Long (676 lines)
- **Scope:** aeo-ux-design
- **File:** `skills/react-pwa-designer/SKILL.md`
- **Problem:** 676-line skill with project setup, templates, React patterns, state management, TypeScript config — should be a 100-200 line skill with @references.
- **Fix:** Reduce to core patterns, move detail to @referenced files.

---

## LOW Severity Issues

### ISSUE 26: aeo-security Hooks Use Wrong Path Variable
- `$CLAUDE_PROJECT_DIR` should be `${CLAUDE_PLUGIN_ROOT}` for bundled scripts.

### ISSUE 27: Agent Changelog Versions Don't Match Frontmatter
- Frontmatter says `0.1.0`, changelogs say `v1.0.0` / `v0.9.0`.

### ISSUE 28: Tools Field Format Inconsistency
- Some use `tools: [Read, Write]`, others `tools: Read, Write`. Standardize on one format.

### ISSUE 29: All Plugins at Version 0.1.0
- No maturity differentiation. Well-developed plugins (aeo-claude, aeo-n8n) same version as empty ones.

### ISSUE 30: Skill Name Inconsistency
- `claude-agent-sdk` skill uses Title Case name vs kebab-case convention.

### ISSUE 31: marketplace.json Categories Too Broad
- 8 of 17 plugins are "development". Need `workflow`, `project-management`, `devops` categories.

### ISSUE 32: Inconsistent Reference Directory Naming
- aeo-python has both `reference/` and `references/` directories.

### ISSUE 33: Unsupported Frontmatter Field in Skill
- aeo-python `python-cli-engineering` declares `allowed-tools:` — not a documented field.

### ISSUE 35: Nested Markdown Fences in Commands
- aeo-requirements commands use quadruple-backtick nesting.

---

## Recommended Fix Priority

### Phase 1: Critical Fixes (immediate)
1. **ISSUE 3** — Create EPCC_BEST_PRACTICES.md (7 broken commands)
2. **ISSUE 4** — Rename EPCC `/prd` to `/epcc-prd`
3. **ISSUE 2** — Global find-replace of invalid tool names
4. **ISSUE 5** — Remove unfilled template placeholders
5. **ISSUE 6+7** — Fix or remove broken aeo-performance hooks
6. **ISSUE 8** — Wire aeo-testing orphaned scripts or document them

### Phase 2: Architecture (short-term)
7. **ISSUE 1** — Design shared agent strategy, eliminate ~50 duplicate files
8. **ISSUE 14** — Strip duplicate agents from EPCC
9. **ISSUE 13** — Merge or enhance aeo-code-analysis
10. **ISSUE 12** — Differentiate testing vs tdd-workflow
11. **ISSUE 15** — Refactor oversized EPCC commands

### Phase 3: Quality Uplift (medium-term)
12. **ISSUE 10** — Tiered model selection across all agents
13. **ISSUE 11** — Standardize agent trigger descriptions
14. **ISSUE 16+17** — Add commands and skills to hollow/knowledge-light plugins
15. **ISSUE 19** — Fix @reference syntax in skills
16. **ISSUE 20+21** — Fix scope mismatches and consolidate overlapping agents

### Phase 4: Marketplace Expansion (long-term)
17. **ISSUE 18** — New plugins for CI/CD, API design, database design
18. **ISSUES 23, 29, 31** — Metadata cleanup (tags, versions, categories)

---

## Plugin Health Matrix

| Plugin | Unique Value | Health | Top Issues |
|--------|-------------|--------|------------|
| **aeo-claude** | 10 unique skills | Good | Minor (no agents/commands) |
| **aeo-n8n** | 7 unique skills | Good | Minor (no agents/commands) |
| **aeo-nous** | Unique system | Good | Version mismatch (#9) |
| **aeo-python** | 3 unique skills | Fair | No interactive entry points (#22) |
| **aeo-documentation** | 5 unique agents, 5 commands | Fair | 7 duplicate agents (#1), invalid tools (#2) |
| **aeo-architecture** | 3 unique agents, 3 commands | Fair | Overlapping variants (#21), invalid tools (#2) |
| **aeo-epcc-workflow** | 7 unique commands | Fair | 12 duplicate agents (#1,14), oversized commands (#15), broken refs (#3) |
| **aeo-requirements** | 2 commands | Fair | /prd collision (#4), no skills (#17) |
| **aeo-security** | 2 commands | Fair | No skills (#17), wrong path var (#26) |
| **aeo-tdd-workflow** | 2 commands | Fair | Overlaps testing (#12), no skills (#17) |
| **aeo-testing** | 1 unique skill | Poor | Empty hooks (#8), overlaps tdd (#12) |
| **aeo-performance** | 1 unique agent | Poor | Broken hooks (#6,7,25), no skills (#17) |
| **aeo-ux-design** | 1 skill, 1 agent | Poor | Scope mismatch (#20), oversized skill (#34) |
| **aeo-agile-tools** | 3 unique agents | Poor | No commands/skills (#16), hollow |
| **aeo-troubleshooting** | 1 command | Poor | Hollow, no skills (#16,17) |
| **aeo-deployment** | 0 unique content | Poor | Single duplicate agent, hollow (#16) |
| **aeo-code-analysis** | 0 unique content | Poor | Fully redundant (#13) |
