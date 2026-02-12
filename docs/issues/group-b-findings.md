# Group B Plugin Quality Review Findings

**Date:** 2026-02-12
**Reviewer:** reviewer-b
**Plugins Reviewed:** aeo-nous, aeo-performance, aeo-python, aeo-requirements, aeo-security, aeo-tdd-workflow, aeo-testing, aeo-troubleshooting, aeo-ux-design

---

## Summary

| Severity | Count |
|----------|-------|
| HIGH     | 12    |
| MEDIUM   | 15    |
| LOW      | 6     |
| **TOTAL**| **33**|

---

### ISSUE GB-1: Non-standard tool names used across all Group B agents
- **Severity:** HIGH
- **Plugin:** aeo-performance, aeo-security, aeo-tdd-workflow, aeo-testing, aeo-troubleshooting, aeo-ux-design, aeo-requirements
- **File(s):** 20+ agent .md files across Group B plugins
- **Problem:** Agent frontmatter declares tools that are not valid Claude Code tools:
  - `MultiEdit` (used in ~15 agents) — should be `Edit`
  - `BashOutput` (used in ~10 agents) — should be `Bash` (which already returns output)
  - `LS` (used in ~8 agents) — should be `Glob` or `Bash` with `ls`
  - `TodoWrite` (used in ~6 agents) — non-standard; use `Write` or task tools
  - `KillBash` (used in 2 agents) — not a standard tool
- **Impact:** Agents may fail when attempting to invoke non-existent tools. At minimum, they waste context declaring capabilities they cannot use.
- **Fix:** Replace with standard Claude Code tools: Read, Write, Edit, Grep, Glob, Bash, WebSearch, WebFetch. Remove MultiEdit, BashOutput, LS, TodoWrite, KillBash.

---

### ISSUE GB-2: Duplicate agent names across plugins cause naming collisions
- **Severity:** HIGH
- **Plugin:** All Group B plugins with agents
- **File(s):** agents/*.md across multiple plugins
- **Problem:** 9 agent names are duplicated across multiple plugins. When multiple plugins are loaded, only the last-loaded version of each agent is active:
  - `code-archaeologist` — 7 copies (aeo-architecture, aeo-code-analysis, aeo-documentation, aeo-epcc-workflow, aeo-performance, aeo-tdd-workflow, aeo-troubleshooting)
  - `business-analyst` — 6 copies (aeo-agile-tools, aeo-documentation, aeo-epcc-workflow, aeo-requirements, aeo-security, aeo-tdd-workflow)
  - `qa-engineer` — 6 copies (aeo-architecture, aeo-epcc-workflow, aeo-security, aeo-tdd-workflow, aeo-testing, aeo-troubleshooting)
  - `system-designer` — 6 copies (aeo-architecture, aeo-documentation, aeo-epcc-workflow, aeo-performance, aeo-security, aeo-testing)
  - `test-generator` — 5 copies (aeo-architecture, aeo-documentation, aeo-epcc-workflow, aeo-tdd-workflow, aeo-testing)
  - `security-reviewer` — 4 copies (aeo-architecture, aeo-epcc-workflow, aeo-security, aeo-tdd-workflow)
  - `performance-profiler` — 3 copies (aeo-architecture, aeo-performance, aeo-tdd-workflow)
  - `ux-optimizer` — 3 copies (aeo-documentation, aeo-epcc-workflow, aeo-ux-design)
  - `optimization-engineer` — 3 copies (aeo-documentation, aeo-epcc-workflow, aeo-performance)
- **Impact:** Unpredictable agent behavior when users install multiple plugins. Silent overwriting of agents with different system prompts.
- **Fix:** Either (a) centralize shared agents in a single plugin (e.g., aeo-core-agents) and reference them, or (b) prefix agent names with plugin context (e.g., `security-qa-engineer`, `tdd-test-generator`).

---

### ISSUE GB-3: Unfilled template placeholders in Pipeline Integration and Edge Cases sections
- **Severity:** HIGH
- **Plugin:** aeo-performance, aeo-requirements, aeo-security, aeo-tdd-workflow, aeo-testing, aeo-troubleshooting
- **File(s):** 18+ agent .md files across Group B (and many more in Group A)
- **Problem:** Agent system prompts contain unfilled template placeholders that were never completed:
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
  Affected Group B agents: business-analyst (3 plugins), code-archaeologist (2 plugins), qa-engineer (4 plugins), test-generator (3 plugins), system-designer, security-reviewer (truncated file)
- **Impact:** These placeholders consume context tokens without providing value. They signal incomplete development to the agent, potentially confusing its self-model.
- **Fix:** Either fill in with actual integration details or remove the placeholder sections entirely.

---

### ISSUE GB-4: aeo-performance hooks reference non-existent Python scripts
- **Severity:** HIGH
- **Plugin:** aeo-performance
- **File(s):** aeo-performance/hooks/hooks.json (lines 79, 96, 101, 106)
- **Problem:** Stop and SubagentStop hooks reference four Python scripts that do not exist anywhere in the plugin:
  - `scripts/calculate_agent_cost.py`
  - `scripts/generate_performance_report.py`
  - `scripts/calculate_session_cost.py`
  - `scripts/identify_bottlenecks.py`
- **Impact:** These hooks will fail at runtime with "file not found" errors, blocking Stop events.
- **Fix:** Create the referenced scripts in the plugin, or change to `${CLAUDE_PLUGIN_ROOT}/hooks/` path prefix with bundled scripts, or remove these hook entries.

---

### ISSUE GB-5: aeo-performance hooks have shell variable expansion errors
- **Severity:** HIGH
- **Plugin:** aeo-performance
- **File(s):** aeo-performance/hooks/hooks.json (lines 37, 57, 67, 79, 84)
- **Problem:** Multiple hook commands use `${file_path}`, `${query}`, `${agent_name}`, `${duration}`, `${model}` variables that are not documented as available in hook context. Additionally, `${file_path}` used inside single-quoted awk strings won't expand:
  ```json
  "command": "wc -l ${file_path} | awk '{print \"FILE_SIZE,${file_path},\"$1}' >> .claude/metrics.log"
  ```
  The `${file_path}` inside `'{...}'` won't be shell-expanded.
- **Impact:** Hooks will either fail or log empty/literal variable names instead of actual values.
- **Fix:** Verify which variables Claude Code provides to hooks via environment or stdin. Fix quoting to allow proper variable expansion.

---

### ISSUE GB-6: aeo-python has no agents, commands, or hooks
- **Severity:** HIGH
- **Plugin:** aeo-python
- **File(s):** Plugin root structure
- **Problem:** The plugin contains only 3 skills (agent-tui-expert, python-cli-engineering, python-data-engineering) with no agents, commands, or hooks. This makes it purely passive reference material with no interactive entry points.
- **Impact:** Users cannot invoke Python expertise through commands (like `/python-scaffold` or `/data-pipeline-init`). Skills only activate via implicit context matching, reducing discoverability.
- **Fix:** Add at least one command (e.g., `/python-init` to scaffold a CLI project) and consider a skill-activating agent.

---

### ISSUE GB-7: aeo-testing hooks.json is empty with orphaned Python files
- **Severity:** HIGH
- **Plugin:** aeo-testing
- **File(s):** aeo-testing/hooks/hooks.json, aeo-testing/hooks/black_formatter.py, aeo-testing/hooks/python_lint.py, aeo-testing/hooks/use_uv.py, aeo-testing/hooks/ruff.toml
- **Problem:** hooks.json contains `"hooks": {}` (empty) but the hooks directory contains four Python scripts and a ruff.toml configuration that are never referenced. The description says "disabled by default" but there's no documented way to enable them.
- **Impact:** Useful quality gate scripts (black formatting, ruff linting, uv enforcement) are present but completely inactive and undiscoverable.
- **Fix:** Either provide a reference configuration in README.md showing how to enable each hook, or add the hooks in a disabled-but-documented state with comments.

---

### ISSUE GB-8: aeo-nous version mismatch between plugin.json and command
- **Severity:** HIGH
- **Plugin:** aeo-nous
- **File(s):** aeo-nous/.claude-plugin/plugin.json (version: 0.1.5), aeo-nous/commands/setup.md (version: 0.3.0)
- **Problem:** The plugin manifest declares version 0.1.5 but the `/nous:setup` command declares version 0.3.0. This creates confusion about the actual plugin state.
- **Impact:** Version tracking is unreliable. Users and tooling cannot determine the true plugin version.
- **Fix:** Synchronize versions across all components to a single source of truth.

---

### ISSUE GB-9: Skills use markdown links instead of @reference syntax for progressive disclosure
- **Severity:** MEDIUM
- **Plugin:** aeo-python, aeo-testing, aeo-ux-design
- **File(s):** aeo-python/skills/*/SKILL.md, aeo-testing/skills/automating-computer-use-testing/SKILL.md, aeo-ux-design/skills/react-pwa-designer/SKILL.md
- **Problem:** All skill files use markdown link syntax `[text](path/to/file.md)` instead of the `@relative/path.md` syntax specified in CLAUDE.md for loading referenced content into Claude's context.
- **Impact:** Referenced content is not automatically loaded into context when the skill activates, reducing the skill's effectiveness. Users must manually navigate to referenced files.
- **Fix:** Replace markdown links to reference files with `@relative/path.md` syntax throughout all SKILL.md files.

---

### ISSUE GB-10: Agent descriptions lack specific trigger examples
- **Severity:** MEDIUM
- **Plugin:** aeo-performance, aeo-requirements, aeo-security, aeo-tdd-workflow, aeo-testing, aeo-troubleshooting
- **File(s):** Multiple agents across Group B plugins
- **Problem:** Many agent descriptions use vague trigger language without concrete activation examples:
  - "Deploy when working with legacy systems..." (code-archaeologist)
  - "Activate during early project phases..." (business-analyst)
  - "Invoke before releases..." (qa-engineer)
  - "Deploy for high-level system planning..." (system-designer)
  These lack the specific example phrases that CLAUDE.md requires (e.g., "Use this agent when... include trigger examples").
- **Impact:** Agents may not be selected reliably by the Task tool when users describe their needs in different terms.
- **Fix:** Add 2-3 concrete trigger examples to each description, e.g., "Use when: 'analyze this legacy codebase', 'map dependencies in this module', 'what does this undocumented code do?'"

---

### ISSUE GB-11: aeo-ux-design scope mismatch — claims accessibility but lacks dedicated tooling
- **Severity:** MEDIUM
- **Plugin:** aeo-ux-design
- **File(s):** aeo-ux-design/.claude-plugin/plugin.json, skills/react-pwa-designer/SKILL.md
- **Problem:** Plugin description claims "accessibility validation, and WCAG compliance verification" but the only skill is react-pwa-designer (React/PWA focused). No dedicated accessibility skill, command, or hook exists. The ux-optimizer agent mentions accessibility in passing but has no supporting knowledge.
- **Impact:** Users expecting accessibility validation tooling will find only general UX/React content.
- **Fix:** Either (a) add a dedicated accessibility/WCAG skill and `/audit-accessibility` command, or (b) revise the plugin description to match actual scope.

---

### ISSUE GB-12: aeo-requirements and aeo-troubleshooting have no skills directory
- **Severity:** MEDIUM
- **Plugin:** aeo-requirements, aeo-troubleshooting
- **File(s):** Plugin root structure
- **Problem:** Neither plugin has a `skills/` directory. Skills provide domain knowledge that is contextually loaded, making agents and commands more effective. Both plugins would benefit from skills:
  - aeo-requirements: requirements writing standards, stakeholder analysis techniques
  - aeo-troubleshooting: debugging methodologies, root cause analysis frameworks
- **Impact:** Agents operate without contextual domain knowledge, relying entirely on their system prompts.
- **Fix:** Add 1-2 skills per plugin covering core domain knowledge.

---

### ISSUE GB-13: aeo-tdd-workflow has no skills or hooks
- **Severity:** MEDIUM
- **Plugin:** aeo-tdd-workflow
- **File(s):** Plugin root structure
- **Problem:** A TDD workflow plugin should enforce the red-green-refactor methodology through hooks (e.g., PreToolUse to warn if tests aren't written first) and provide domain knowledge via skills (TDD best practices, coverage targets). Neither exists.
- **Impact:** TDD enforcement is purely advisory through agent prompts, with no automation to prevent workflow violations.
- **Fix:** Add hooks for TDD enforcement (e.g., check test files exist before implementation) and skills documenting TDD patterns.

---

### ISSUE GB-14: security-reviewer agent file truncated
- **Severity:** MEDIUM
- **Plugin:** aeo-security, aeo-tdd-workflow
- **File(s):** aeo-security/agents/security-reviewer.md, aeo-tdd-workflow/agents/security-reviewer.md
- **Problem:** The security-reviewer.md file ends abruptly at ~line 108 without Pipeline Integration, Edge Cases, or Changelog sections present in all other agents.
- **Impact:** Agent is missing integration guidance and failure mode documentation.
- **Fix:** Complete the file with Pipeline Integration, Edge Cases, and Changelog sections.

---

### ISSUE GB-15: aeo-performance agents missing Write tool
- **Severity:** MEDIUM
- **Plugin:** aeo-performance
- **File(s):** aeo-performance/agents/optimization-engineer.md, aeo-performance/agents/performance-profiler.md, aeo-performance/agents/performance-optimizer.md
- **Problem:** Three agents that generate reports, baselines, and documentation don't include the `Write` tool in their frontmatter. Their system prompts describe writing performance reports and baseline files.
- **Impact:** Agents cannot create new files as their prompts instruct them to do.
- **Fix:** Add `Write` to the tools list for these agents.

---

### ISSUE GB-16: Inconsistent tools array format across agents
- **Severity:** MEDIUM
- **Plugin:** aeo-security, aeo-tdd-workflow, aeo-testing, aeo-troubleshooting
- **File(s):** qa-engineer.md, security-reviewer.md across multiple plugins
- **Problem:** Some agents use array bracket syntax `tools: [Read, Write, ...]` while others use comma-separated string `tools: Read, Write, ...`. Both may work but inconsistency reduces maintainability.
- **Impact:** Makes bulk validation harder; could cause parsing issues with strict validators.
- **Fix:** Standardize on one format (comma-separated string per CLAUDE.md examples).

---

### ISSUE GB-17: aeo-performance hooks use non-standard echo-to-stderr pattern
- **Severity:** MEDIUM
- **Plugin:** aeo-performance
- **File(s):** aeo-performance/hooks/hooks.json (lines 10, 21, 32, 47)
- **Problem:** PreToolUse and PostToolUse hooks emit messages to stderr with `echo '...' >&2`. These messages appear in the user's terminal but provide no actionable value ("Read operation started", "Command started", etc.).
- **Impact:** Noisy stderr output on every Read and Bash operation without clear benefit. Users will see these messages but can't act on them.
- **Fix:** Either remove the echo hooks (they're debugging scaffolding) or redirect output to a log file.

---

### ISSUE GB-18: aeo-ux-design react-pwa-designer skill is excessively long (676 lines)
- **Severity:** MEDIUM
- **Plugin:** aeo-ux-design
- **File(s):** aeo-ux-design/skills/react-pwa-designer/SKILL.md
- **Problem:** The skill file is 676 lines containing project setup, templates, React patterns, state management, TypeScript config, and PWA implementation. This is a comprehensive guide rather than a contextual skill trigger.
- **Impact:** Loading this entire skill into context consumes significant tokens. Much of the content is reference material that should be loaded on-demand via @references.
- **Fix:** Reduce SKILL.md to core patterns and decision guidance (~100-200 lines), moving detailed implementation to @referenced files.

---

### ISSUE GB-19: aeo-python python-cli-engineering has inconsistent reference directory naming
- **Severity:** MEDIUM
- **Plugin:** aeo-python
- **File(s):** aeo-python/skills/python-cli-engineering/SKILL.md (line 248), aeo-python/skills/python-cli-engineering/reference/ vs references/
- **Problem:** The skill directory contains both `reference/` (singular, with database-migrations.md) and `references/` (plural, with tech-stack.md, architecture.md, configuration.md). SKILL.md links to `reference/database-migrations.md` which exists, but the inconsistent naming is confusing.
- **Impact:** Contributors may create files in the wrong directory. Pattern is unclear.
- **Fix:** Consolidate to a single `references/` directory (plural, matching the majority pattern).

---

### ISSUE GB-20: aeo-python python-cli-engineering declares unsupported frontmatter field
- **Severity:** MEDIUM
- **Plugin:** aeo-python
- **File(s):** aeo-python/skills/python-cli-engineering/SKILL.md (line 4)
- **Problem:** Skill declares `allowed-tools: Read, Write, Edit, Bash` which is not a documented frontmatter field per CLAUDE.md. The other two skills in the plugin don't declare this field.
- **Impact:** Field is likely ignored by the plugin system, creating a false sense of tool restriction.
- **Fix:** Remove the field, or verify it's supported by the runtime.

---

### ISSUE GB-21: aeo-ux-design has no commands directory
- **Severity:** MEDIUM
- **Plugin:** aeo-ux-design
- **File(s):** Plugin root structure
- **Problem:** No slash commands exist despite the plugin having two agents and a rich skill. Commands like `/create-design-system`, `/audit-accessibility`, `/generate-components` would provide user-facing entry points.
- **Impact:** Users have no direct way to invoke UX design capabilities. Must rely on agents being auto-selected.
- **Fix:** Add at least one command (e.g., `/design-component` or `/audit-ux`).

---

### ISSUE GB-22: Agent changelog versions don't match frontmatter versions
- **Severity:** LOW
- **Plugin:** aeo-performance, aeo-requirements, aeo-security, aeo-tdd-workflow, aeo-testing, aeo-troubleshooting
- **File(s):** Most agent .md files across Group B
- **Problem:** Agent frontmatter declares `version: 0.1.0` but changelogs show `v1.0.0 (2025-08-07)` and `v0.9.0 (2025-08-02)`. The versions are contradictory.
- **Impact:** Version tracking is unreliable across agents.
- **Fix:** Align changelog versions with frontmatter version field.

---

### ISSUE GB-23: aeo-nous hooks use potentially unsupported event names
- **Severity:** LOW
- **Plugin:** aeo-nous
- **File(s):** aeo-nous/hooks/hooks.json
- **Problem:** Uses `SessionStart`, `SessionEnd`, `PreCompact`, and `Notification` event names. The previous audit (Issue #3) listed the valid events as PreToolUse, PostToolUse, Stop, UserPromptSubmit, SubagentStop plus SessionStart and SessionEnd. However, `PreCompact` and `Notification` are less commonly documented and may not be supported in all Claude Code versions.
- **Impact:** If unsupported, the hook-profiler.sh won't fire on PreCompact/Notification events (silent failure).
- **Fix:** Verify these events work in current Claude Code runtime. The CLAUDE.md for this repo lists them as valid (PreCompact, Notification), but they should be tested.

---

### ISSUE GB-24: aeo-security hooks reference $CLAUDE_PROJECT_DIR scripts
- **Severity:** LOW
- **Plugin:** aeo-security
- **File(s):** aeo-security/hooks/hooks.json (lines 10, 20)
- **Problem:** Hooks reference `$CLAUDE_PROJECT_DIR/hooks/security_check.py` and `$CLAUDE_PROJECT_DIR/hooks/command_security_check.sh`. The actual scripts ship at `${CLAUDE_PLUGIN_ROOT}/hooks/` (the plugin directory), not `$CLAUDE_PROJECT_DIR` (the user's project directory).
- **Impact:** Hooks will look for scripts in the user's project directory, not the plugin directory. Will fail unless users manually copy scripts.
- **Fix:** Change `$CLAUDE_PROJECT_DIR` to `${CLAUDE_PLUGIN_ROOT}` so hooks use the plugin's bundled scripts.

---

### ISSUE GB-25: aeo-requirements prd.md and tech-req.md use nested markdown fences
- **Severity:** LOW
- **Plugin:** aeo-requirements
- **File(s):** aeo-requirements/commands/prd.md, aeo-requirements/commands/tech-req.md
- **Problem:** Commands embed quadruple-backtick markdown fences (````markdown`) inside the command body. This unusual nesting may confuse some markdown parsers or the Claude Code command loader.
- **Impact:** Potential parsing issues when command body is processed; template sections may not render correctly.
- **Fix:** Use alternative delimiters or restructure to avoid deeply nested fences.

---

### ISSUE GB-26: aeo-python python-data-engineering description lacks action trigger word
- **Severity:** LOW
- **Plugin:** aeo-python
- **File(s):** aeo-python/skills/python-data-engineering/SKILL.md (frontmatter)
- **Problem:** Description ends with "Reference for API-to-database flows or dimensional modeling" — passive phrasing without an action trigger like "Apply when" or "Engage when" that the other two skills use.
- **Impact:** Slightly lower activation reliability compared to sibling skills.
- **Fix:** Change to "Engage when building API-to-database flows or dimensional models with Python and PostgreSQL."

---

### ISSUE GB-27: aeo-ux-design skill references non-standard MCP tool syntax
- **Severity:** LOW
- **Plugin:** aeo-ux-design
- **File(s):** aeo-ux-design/skills/react-pwa-designer/SKILL.md (lines ~413-445)
- **Problem:** Skill documents MCP tools using TypeScript-style syntax (`mcp__context7__resolve_library_id()`, `mcp__shadcn__getComponents()`) that is non-standard and inconsistent with other plugins.
- **Impact:** May confuse users or Claude about how to invoke MCP tools.
- **Fix:** Use standard MCP tool invocation documentation format or note these as examples requiring specific MCP server configuration.

---

## Cross-Plugin Patterns Observed

### Pattern 1: Template-Based Agent Generation
All 9 Group B plugins appear to have been generated from the same agent template. Evidence:
- Identical unfilled `[Required inputs]`/`[Expected outputs]` placeholders across 30+ agents
- Same changelog format with identical dates (2025-08-07, 2025-08-02)
- Identical character naming pattern (CodeDigger, OptimizeWiz, ProfileMaster, etc.)
- Same Pipeline Integration section structure copied verbatim

### Pattern 2: Skill-Light Plugins
5 of 9 Group B plugins have zero or one skill, making them agent-heavy but knowledge-light:
- aeo-requirements: 0 skills
- aeo-tdd-workflow: 0 skills
- aeo-troubleshooting: 0 skills
- aeo-security: 0 skills
- aeo-performance: 0 skills

### Pattern 3: Hook Inconsistency
Hook quality varies wildly across Group B:
- aeo-nous: Well-structured, functional hooks (best in group)
- aeo-security: Clean hooks with proper matchers
- aeo-performance: Hooks with broken script references and variable expansion issues
- aeo-testing: Empty hooks with orphaned scripts
- aeo-requirements, aeo-tdd-workflow, aeo-troubleshooting, aeo-python, aeo-ux-design: No hooks at all
