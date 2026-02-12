# Group A Plugin Quality Findings

## Summary

| Plugin | Issues Found | Severity Breakdown |
|--------|-------------|-------------------|
| aeo-agile-tools | 3 | 1 HIGH, 1 MEDIUM, 1 LOW |
| aeo-architecture | 3 | 1 HIGH, 1 MEDIUM, 1 LOW |
| aeo-claude | 1 | 1 LOW |
| aeo-code-analysis | 3 | 1 HIGH, 1 MEDIUM, 1 LOW |
| aeo-deployment | 3 | 1 HIGH, 1 MEDIUM, 1 LOW |
| aeo-documentation | 4 | 2 HIGH, 1 MEDIUM, 1 LOW |
| aeo-epcc-workflow | 6 | 3 HIGH, 2 MEDIUM, 1 LOW |
| aeo-n8n | 1 | 1 LOW |
| **Cross-cutting** | **3** | **2 HIGH, 1 MEDIUM** |
| **TOTAL** | **27** | **9 HIGH, 6 MEDIUM, 12 LOW** |

---

## Cross-Cutting Issues

### ISSUE GA-1: Every single agent uses opus model with no differentiation
- **Severity:** HIGH
- **Plugin:** ALL plugins with agents (agile-tools, architecture, code-analysis, deployment, documentation, epcc-workflow)
- **File(s):** All 52+ agent `.md` files across Group A plugins
- **Problem:** Every agent across all Group A plugins specifies `model: opus`. There is zero differentiation based on task complexity. Agents performing simple focused tasks (e.g., code-archaeologist doing read-only analysis, test-generator writing boilerplate tests) use the same expensive model as complex reasoning agents (system-designer, architect).
- **Impact:** Unnecessary cost for users. Opus is the most expensive model and many agent tasks (documentation lookup, code search, test scaffolding) can be handled well by sonnet or haiku.
- **Fix:** Audit each agent's actual task complexity. Recommend: `opus` for complex multi-step reasoning (architect, system-designer, security-reviewer), `sonnet` for focused generation tasks (test-generator, documentation-agent, code-archaeologist), `haiku` for simple retrieval/formatting tasks.

### ISSUE GA-2: Invalid tool names used across 30+ agents marketplace-wide
- **Severity:** HIGH
- **Plugin:** agile-tools, architecture, code-analysis, deployment, documentation, epcc-workflow
- **File(s):** See per-plugin findings for specific files
- **Problem:** The following non-existent tools appear in agent frontmatter:
  - `MultiEdit` - used in 20+ agents (not a valid Claude Code tool; use `Edit` instead)
  - `LS` - used in 15+ agents (not a valid tool; use `Glob` or `Bash` with `ls`)
  - `BashOutput` - used in 10+ agents (not a valid tool; `Bash` already returns output)
  - `KillBash` - used in 2 agents (not a valid tool; no equivalent needed)
  - `TodoWrite` - used in 6 agents (not a valid tool; use `TaskCreate`/`TaskUpdate` or remove)
- **Impact:** Agents declare capabilities they don't have. Claude Code ignores invalid tool names, so agents silently lack intended functionality. Users may expect behavior that never works.
- **Fix:** Replace all invalid tools: `MultiEdit` → `Edit`, `LS` → `Glob`, `BashOutput` → remove (Bash suffices), `KillBash` → remove, `TodoWrite` → remove or replace with `TaskCreate`. Also fix the CLAUDE.md example (line 33) which shows `LS` as a valid tool — this is likely the source of the pattern.

### ISSUE GA-3: Massive agent duplication — aeo-epcc-workflow copies agents from 5 other plugins
- **Severity:** HIGH
- **Plugin:** aeo-epcc-workflow (primary), aeo-documentation, aeo-architecture, aeo-agile-tools, aeo-code-analysis, aeo-deployment
- **File(s):** All 12 agents in `aeo-epcc-workflow/agents/`
- **Problem:** aeo-epcc-workflow contains 12 agents that are **byte-for-byte identical** copies from other plugins:
  - `system-designer.md` — identical to aeo-architecture and aeo-documentation
  - `code-archaeologist.md` — identical to aeo-architecture, aeo-documentation, aeo-code-analysis
  - `project-manager.md` — identical to aeo-agile-tools
  - `business-analyst.md` — identical to aeo-documentation and aeo-agile-tools
  - `deployment-agent.md` — identical to aeo-deployment
  - `documentation-agent.md` — identical to aeo-documentation
  - `optimization-engineer.md` — identical to aeo-documentation
  - `qa-engineer.md` — identical to aeo-architecture
  - `security-reviewer.md` — identical to aeo-architecture
  - `tech-evaluator.md` — identical to aeo-code-analysis
  - `test-generator.md` — identical to aeo-architecture and aeo-documentation
  - `ux-optimizer.md` — identical to aeo-documentation

  Similarly, aeo-documentation duplicates 5 agents from aeo-architecture:
  - `architecture-documenter.md`, `code-archaeologist.md`, `system-designer.md`, `test-generator.md`, `business-analyst.md` (from aeo-agile-tools)
- **Impact:** Maintenance nightmare — fixing a bug in one agent requires finding and updating all copies. Users loading multiple plugins get agent name conflicts. The marketplace appears larger than it actually is (inflated component count).
- **Fix:** Either (a) use a shared agents mechanism / cross-plugin references, (b) keep agents only in their canonical "home" plugin and remove duplicates, or (c) if EPCC is meant to be a "batteries-included" mega-plugin, document that clearly and mark the others as modular alternatives.

---

## Per-Plugin Findings

### aeo-agile-tools

#### ISSUE GA-4: Invalid tool `TodoWrite` in all 4 agents
- **Severity:** HIGH
- **Plugin:** aeo-agile-tools
- **File(s):** `agents/project-manager.md`, `agents/product-owner.md`, `agents/scrum-master.md`, `agents/business-analyst.md`
- **Problem:** All 4 agents specify `TodoWrite` in their tools list. `TodoWrite` is not a valid Claude Code tool.
- **Impact:** Agents cannot create/manage task lists as intended. The tool name is silently ignored.
- **Fix:** Remove `TodoWrite` or replace with `TaskCreate` if task tracking is needed. Add `Glob` to agents that need file discovery.

#### ISSUE GA-5: Hooks disabled but file still present
- **Severity:** MEDIUM
- **Plugin:** aeo-agile-tools
- **File(s):** `hooks/hooks.json`
- **Problem:** Hooks were intentionally disabled per recent commits (opinionated hooks removed). The file still exists with `"hooks": {}` and a description saying "Scrum ceremony and sprint management automation". The description doesn't match the empty content.
- **Impact:** Confusing for users — description implies functionality that isn't there.
- **Fix:** Update description to indicate hooks are disabled by default, or remove the file if hooks aren't planned.

#### ISSUE GA-6: No skills directory
- **Severity:** LOW
- **Plugin:** aeo-agile-tools
- **File(s):** N/A (missing directory)
- **Problem:** Plugin has agents but no skills. Agile methodology knowledge (Scrum ceremonies, sprint planning, estimation techniques) would be valuable as contextual skills.
- **Impact:** Agents lack reusable domain knowledge. Each agent must encode all agile knowledge in its system prompt.
- **Fix:** Consider adding skills for core agile concepts that agents can reference.

---

### aeo-architecture

#### ISSUE GA-7: Invalid tools `MultiEdit` and `LS` in 9 of 10 agents
- **Severity:** HIGH
- **Plugin:** aeo-architecture
- **File(s):** `agents/system-designer.md`, `agents/architect.md`, `agents/simple-architect.md`, `agents/simple-architecture-documenter.md`, `agents/performance-profiler.md`, `agents/security-reviewer.md`, `agents/qa-engineer.md`, `agents/architecture-documenter.md`, `agents/code-archaeologist.md`, `agents/test-generator.md`
- **Problem:** Invalid tools used across agents:
  - `MultiEdit`: system-designer, architect, simple-architect, simple-architecture-documenter, architecture-documenter, qa-engineer, test-generator, performance-profiler
  - `LS`: system-designer, architect, simple-architect, simple-architecture-documenter, architecture-documenter, code-archaeologist, security-reviewer
  - `BashOutput`: qa-engineer, security-reviewer, test-generator, performance-profiler
- **Impact:** Agents declare capabilities they don't have.
- **Fix:** `MultiEdit` → `Edit`, `LS` → `Glob`, `BashOutput` → remove.

#### ISSUE GA-8: Redundant architect variants without clear differentiation
- **Severity:** MEDIUM
- **Plugin:** aeo-architecture
- **File(s):** `agents/architect.md`, `agents/simple-architect.md`, `agents/system-designer.md`, `agents/simple-architecture-documenter.md`, `agents/architecture-documenter.md`
- **Problem:** 5 agents cover overlapping territory (architecture design and documentation). The trigger descriptions don't clearly differentiate when to use `architect` vs `simple-architect` vs `system-designer`, or `architecture-documenter` vs `simple-architecture-documenter`.
- **Impact:** Users and Claude Code's routing can't distinguish which agent to trigger. Agent selection becomes arbitrary.
- **Fix:** Consolidate to 2-3 agents with clearly distinct purposes, or sharpen trigger descriptions to make selection unambiguous. Consider: one for design, one for documentation, one for review.

#### ISSUE GA-9: Only 1 skill for 10 agents
- **Severity:** LOW
- **Plugin:** aeo-architecture
- **File(s):** `skills/mcp-architect-designer/SKILL.md`
- **Problem:** The single skill is specifically about MCP architecture. General architecture patterns (C4 model, ADR templates, design patterns) are not captured as reusable skills.
- **Impact:** Architecture domain knowledge is scattered across agent system prompts instead of being shared via skills.
- **Fix:** Extract common architecture knowledge into skills (e.g., c4-modeling, adr-templates, design-patterns).

---

### aeo-claude

#### ISSUE GA-10: No agents — skills-only plugin
- **Severity:** LOW
- **Plugin:** aeo-claude
- **File(s):** N/A
- **Problem:** Plugin has 9 skills, 0 agents, 0 commands. The skills are well-structured (ultrareview, ultraplan, opus-prompting, etc.) but are only accessible as contextual skills, not as invocable commands or autonomous agents.
- **Impact:** Minor — skills are designed to be contextually loaded, which is valid. However, skills like `ultrareview` and `ultraplan` would benefit from command wrappers for explicit invocation.
- **Fix:** Consider adding slash commands that explicitly invoke the key skills (e.g., `/ultrareview`, `/ultraplan`). Note: these already appear as registered skills in the system, so this may be working as intended.

---

### aeo-code-analysis

#### ISSUE GA-11: Invalid tool `LS` in code-archaeologist, `MultiEdit` in tech-evaluator
- **Severity:** HIGH
- **Plugin:** aeo-code-analysis
- **File(s):** `agents/code-archaeologist.md`, `agents/tech-evaluator.md`
- **Problem:** `code-archaeologist.md` uses `LS` (invalid). `tech-evaluator.md` uses `MultiEdit` (invalid).
- **Impact:** Agents lack intended capabilities.
- **Fix:** `LS` → `Glob`, `MultiEdit` → `Edit`.

#### ISSUE GA-12: Both agents are exact duplicates from other plugins
- **Severity:** MEDIUM
- **Plugin:** aeo-code-analysis
- **File(s):** `agents/code-archaeologist.md`, `agents/tech-evaluator.md`
- **Problem:** `code-archaeologist.md` is identical to the copy in aeo-architecture, aeo-documentation, and aeo-epcc-workflow. `tech-evaluator.md` is identical to aeo-epcc-workflow's copy. The plugin adds no unique agents.
- **Impact:** Plugin exists primarily as a duplicate container. Users installing both aeo-architecture and aeo-code-analysis get agent name conflicts.
- **Fix:** Either add unique analysis-specific agents (e.g., complexity-analyzer, dependency-mapper) that justify the plugin's existence, or merge into aeo-architecture.

#### ISSUE GA-13: No skills or commands
- **Severity:** LOW
- **Plugin:** aeo-code-analysis
- **File(s):** N/A (missing directories)
- **Problem:** Plugin has only 2 agents (both duplicates), no skills, no commands. It lacks the depth expected of a "code analysis" plugin.
- **Impact:** Plugin doesn't deliver sufficient value as a standalone offering.
- **Fix:** Add code analysis skills (complexity metrics, dependency analysis, code smell detection) and commands (e.g., `/analyze-code`, `/find-tech-debt`).

---

### aeo-deployment

#### ISSUE GA-14: Invalid tools `BashOutput` and `KillBash` in deployment-agent
- **Severity:** HIGH
- **Plugin:** aeo-deployment
- **File(s):** `agents/deployment-agent.md`
- **Problem:** Agent specifies `BashOutput` and `KillBash` — neither is a valid Claude Code tool.
- **Impact:** Agent can't monitor long-running commands or kill stuck processes as intended.
- **Fix:** Remove `BashOutput` (Bash returns output natively), remove `KillBash` (not available). Add `Glob` for file discovery.

#### ISSUE GA-15: Empty hooks with misleading description
- **Severity:** MEDIUM
- **Plugin:** aeo-deployment
- **File(s):** `hooks/hooks.json`
- **Problem:** Hooks object is empty `{}` but description says "Compliance and regulatory validation — disabled by default (see README.md for reference configuration)". There is no README.md in the hooks directory.
- **Impact:** Description references a non-existent README. Users expecting compliance hooks find nothing.
- **Fix:** Either add the referenced README.md with example hook configurations, or update the description to be accurate.

#### ISSUE GA-16: Single-agent plugin with no skills or commands
- **Severity:** LOW
- **Plugin:** aeo-deployment
- **File(s):** N/A
- **Problem:** Plugin contains only 1 agent (deployment-agent), no skills, no commands. For a deployment plugin, expected content would include deployment checklists, rollback procedures, CI/CD patterns.
- **Impact:** Thin plugin that doesn't justify standalone existence.
- **Fix:** Add deployment skills (CI/CD patterns, rollback strategies, blue-green deployment) and commands (e.g., `/deploy-checklist`, `/rollback-plan`).

---

### aeo-documentation

#### ISSUE GA-17: Invalid tools `MultiEdit` and `LS` in 10 of 12 agents
- **Severity:** HIGH
- **Plugin:** aeo-documentation
- **File(s):** `agents/documentation-agent.md`, `agents/docs-tutorial-agent.md`, `agents/docs-howto-agent.md`, `agents/docs-reference-agent.md`, `agents/docs-explanation-agent.md`, `agents/system-designer.md`, `agents/architecture-documenter.md`, `agents/code-archaeologist.md`, `agents/test-generator.md`, `agents/optimization-engineer.md`, `agents/ux-optimizer.md`, `agents/business-analyst.md`
- **Problem:** Multiple invalid tools used across agents:
  - `MultiEdit`: documentation-agent, docs-tutorial-agent, docs-howto-agent, docs-reference-agent, docs-explanation-agent, system-designer, architecture-documenter, test-generator, optimization-engineer, ux-optimizer
  - `LS`: documentation-agent, docs-tutorial-agent, docs-howto-agent, docs-reference-agent, docs-explanation-agent, system-designer, architecture-documenter, code-archaeologist
  - `BashOutput`: test-generator, optimization-engineer
  - `TodoWrite`: business-analyst
- **Impact:** Documentation agents meant to write comprehensive docs are missing editing capabilities they think they have.
- **Fix:** Replace all invalid tools as specified in GA-2.

#### ISSUE GA-18: 7 of 12 agents are duplicates from other plugins
- **Severity:** HIGH
- **Plugin:** aeo-documentation
- **File(s):** `agents/system-designer.md`, `agents/architecture-documenter.md`, `agents/code-archaeologist.md`, `agents/test-generator.md`, `agents/business-analyst.md`, `agents/optimization-engineer.md`, `agents/ux-optimizer.md`
- **Problem:** These 7 agents are byte-for-byte identical to copies in aeo-architecture, aeo-agile-tools, or other plugins. Only 5 agents are unique to documentation: `documentation-agent.md`, `docs-tutorial-agent.md`, `docs-howto-agent.md`, `docs-reference-agent.md`, `docs-explanation-agent.md`.
- **Impact:** Plugin is 58% duplicated content. Maintenance burden multiplied.
- **Fix:** Remove duplicated agents. Keep only the 5 documentation-specific agents. If cross-plugin agent access is needed, implement a reference mechanism.

#### ISSUE GA-19: Diataxis doc agents all use opus for focused single-type tasks
- **Severity:** MEDIUM
- **Plugin:** aeo-documentation
- **File(s):** `agents/docs-tutorial-agent.md`, `agents/docs-howto-agent.md`, `agents/docs-reference-agent.md`, `agents/docs-explanation-agent.md`
- **Problem:** Each Diataxis-type agent (tutorial, howto, reference, explanation) handles one specific documentation style. These are focused generation tasks that don't require complex reasoning.
- **Impact:** Unnecessary cost — sonnet would handle these effectively.
- **Fix:** Change model to `sonnet` for all 4 Diataxis agents.

#### ISSUE GA-20: docs-create command is 612 lines
- **Severity:** LOW
- **Plugin:** aeo-documentation
- **File(s):** `commands/docs-create.md`
- **Problem:** Command file is very long at 612 lines. While not as extreme as EPCC commands, it's still large for a command prompt.
- **Impact:** Large context injection on every invocation. May impact response quality due to instruction volume.
- **Fix:** Consider breaking into focused sub-commands or using progressive disclosure with @references.

---

### aeo-epcc-workflow

#### ISSUE GA-21: 12 agents are all identical duplicates from other plugins
- **Severity:** HIGH
- **Plugin:** aeo-epcc-workflow
- **File(s):** All 12 files in `agents/`
- **Problem:** Every single agent in aeo-epcc-workflow is a byte-for-byte identical copy from another plugin (see GA-3 for full mapping). The plugin adds zero unique agents. It appears to be a "mega-plugin" that bundles agents from aeo-architecture, aeo-documentation, aeo-agile-tools, aeo-code-analysis, and aeo-deployment.
- **Impact:** Users who install aeo-epcc-workflow alongside any source plugin get duplicate agents. The 12 agents also inherit all the invalid tool issues from their sources.
- **Fix:** Either (a) remove duplicate agents and document that EPCC workflow depends on other plugins, or (b) formally declare EPCC as a batteries-included bundle and deprecate the source plugins, or (c) create EPCC-specific agent variants with workflow-aware prompts.

#### ISSUE GA-22: Invalid tools across all 12 agents (inherited from sources)
- **Severity:** HIGH
- **Plugin:** aeo-epcc-workflow
- **File(s):** All agents — `MultiEdit` (8 agents), `LS` (5 agents), `BashOutput` (6 agents), `KillBash` (1 agent), `TodoWrite` (2 agents)
- **Problem:** All 12 copied agents carry their source plugins' invalid tool declarations.
- **Impact:** Compounded by the duplication — fixing tools in source plugins doesn't fix them here.
- **Fix:** Fix in tandem with GA-2 and GA-3.

#### ISSUE GA-23: Hook scripts referenced but don't exist
- **Severity:** HIGH
- **Plugin:** aeo-epcc-workflow
- **File(s):** `hooks/hooks.json`
- **Problem:** Hooks reference two scripts that don't exist in the repository:
  - `$CLAUDE_PROJECT_DIR/hooks/auto_format.py` (PostToolUse on Edit)
  - `$CLAUDE_PROJECT_DIR/hooks/auto_chmod.sh` (PostToolUse on Write)
- **Impact:** Hooks will fail silently or throw errors on every Edit/Write operation. The auto-formatting and auto-chmod functionality described by the hooks is non-functional.
- **Fix:** Either create the missing scripts or remove the broken hook entries. Keep the simple echo hooks for Bash/Stop/SubagentStop if desired.

#### ISSUE GA-24: Commands are extremely long (630-1378 lines each)
- **Severity:** MEDIUM
- **Plugin:** aeo-epcc-workflow
- **File(s):** `commands/trd.md` (1378 lines), `commands/prd.md` (824 lines), `commands/epcc-explore.md` (785 lines), `commands/epcc-code.md` (794 lines), `commands/epcc-plan.md` (630 lines), `commands/epcc-commit.md` (631 lines), `commands/epcc-resume.md` (631 lines)
- **Problem:** Every command is 630+ lines. The TRD command alone is 1378 lines. These are injected as full prompts into context on invocation.
- **Impact:** Massive context consumption per command invocation. Leaves less room for actual work. May degrade response quality due to instruction overload.
- **Fix:** Refactor commands to use progressive disclosure: keep commands concise (under 200 lines) with @references to detailed sub-files that are loaded only when needed.

#### ISSUE GA-25: No skills directory despite being a methodology plugin
- **Severity:** MEDIUM
- **Plugin:** aeo-epcc-workflow
- **File(s):** N/A (missing directory)
- **Problem:** EPCC is a complete development methodology (Explore-Plan-Code-Commit) but has no skills. The methodology knowledge is entirely embedded in the oversized commands.
- **Impact:** Knowledge can't be shared across agents or loaded contextually. Commands must re-explain concepts every time.
- **Fix:** Extract EPCC methodology concepts into skills (e.g., epcc-methodology overview, code review standards, commit conventions) that commands and agents can reference.

#### ISSUE GA-26: Bash echo hooks add noise without value
- **Severity:** LOW
- **Plugin:** aeo-epcc-workflow
- **File(s):** `hooks/hooks.json`
- **Problem:** Three hooks just echo messages to stderr: `'Bash command completed'`, `'Session completed'`, `'Subagent completed'`. These provide no functional value.
- **Impact:** Minor stderr noise. Not harmful but adds no value.
- **Fix:** Remove the echo-only hooks or replace with functional hooks (e.g., logging, timing).

---

### aeo-n8n

#### ISSUE GA-27: Plugin has no agents or commands — skills only
- **Severity:** LOW
- **Plugin:** aeo-n8n
- **File(s):** N/A
- **Problem:** Plugin contains 7 high-quality skills covering n8n workflow automation but has no agents or commands. Skills are well-structured with progressive disclosure via reference files.
- **Impact:** Minor — skills-only is a valid design for domain knowledge plugins. The n8n skills are among the highest quality in the marketplace.
- **Fix:** Consider adding a `/n8n-workflow` command that orchestrates skill selection, or an n8n-expert agent that leverages all 7 skills. Low priority — current design works.

---

## Statistics

- **Total issues found:** 27
- **HIGH severity:** 9 (33%)
- **MEDIUM severity:** 6 (22%)
- **LOW severity:** 12 (44%)

### Issues by Category
| Category | Count | Issues |
|----------|-------|--------|
| Invalid tool names | 7 | GA-2, GA-4, GA-7, GA-11, GA-14, GA-17, GA-22 |
| Agent duplication | 4 | GA-3, GA-12, GA-18, GA-21 |
| Model choice (opus overuse) | 2 | GA-1, GA-19 |
| Missing/broken hooks | 3 | GA-5, GA-15, GA-23 |
| Oversized commands | 2 | GA-20, GA-24 |
| Missing components | 5 | GA-6, GA-9, GA-13, GA-16, GA-25 |
| Low-value content | 2 | GA-26, GA-27 |
| Agent differentiation | 1 | GA-8 |
| Skills-only design | 1 | GA-10 |

### Top 3 Systemic Issues
1. **Invalid tool names** (affects 6 of 8 plugins, 30+ agent files) — Root cause likely in CLAUDE.md example showing `LS` as valid
2. **Massive agent duplication** (aeo-epcc-workflow has 12/12 duplicates, aeo-documentation has 7/12) — No cross-plugin reference mechanism
3. **Universal opus model** (every agent across all plugins uses opus) — No cost/complexity differentiation
