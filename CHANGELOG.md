# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-02-12

### Fixed

- Fix ultrareview-loop Stop hook claiming orphaned state files from other sessions (transcript-gated claiming)
- Fix infinite block cycle when model rejects a foreign loop with no summary block (token-gated blocking)

## [0.4.0] - 2026-02-12

### Added
- 10 new skills across 5 plugins: requirements-elicitation, build-vs-buy (aeo-requirements); red-green-refactor, test-design-patterns (aeo-tdd-workflow); systematic-debugging, common-failure-patterns (aeo-troubleshooting); owasp-top-10, secure-coding (aeo-security); profiling-guide, optimization-patterns (aeo-performance)
- 4 new commands: /sprint-planning, /retrospective (aeo-agile-tools); /deploy-checklist, /release-notes (aeo-deployment)
- 16 EPCC reference files for progressive disclosure of templates and patterns

### Changed
- Bump 14 plugin versions from 0.1.0 to 0.2.0 to reflect rounds 1–3 changes
- Restructure 7 EPCC commands from 628–1376 lines to under 400 lines each via @reference extraction
- Restructure react-pwa-designer skill from 676 to 167 lines using existing reference files
- Replace markdown links with @reference syntax in 4 skill files (31 replacements)
- Enrich marketplace.json tags for feature discoverability

### Fixed
- Sync aeo-nous version to 0.3.0 across plugin.json and setup command
- Remove unsupported `allowed-tools` field from python-cli-engineering skill
- Fix orphaned markdown fence in aeo-requirements tech-req command
- Fix `/prd` → `/epcc-prd` in usage examples (stale from v0.2.0 rename)
- Deduplicate @reference calls across 7 EPCC commands

### Removed
- Placeholder changelog sections with fake version numbers from 16 agent files

## [0.3.0] - 2026-02-12

### Removed

- 40 duplicate agent files across 12 plugins; each agent now exists in exactly one canonical plugin
- aeo-code-analysis plugin (zero unique content after deduplication)
- Empty agents/ directories from aeo-epcc-workflow, aeo-tdd-workflow, aeo-troubleshooting

### Changed

- Agent model tiering: opus for complex reasoning (architect, simple-architect, system-designer, performance-optimizer), haiku for read-only analysis (code-archaeologist), sonnet for all others
- Standardize all 25 agent descriptions to "Use this agent when [scenario]. Examples: ..." pattern
- Normalize tools field format from array syntax to comma-separated across all agents

### Fixed

- Wire aeo-testing hooks to existing quality scripts (black_formatter.py, python_lint.py, use_uv.py)
- Remove residual `MultiEdit` from aeo-security hooks matcher and aeo-testing hook scripts

### Added

- Cross-plugin companion requirements in plugin.json for 6 plugins that reference agents in other plugins

## [0.2.0] - 2026-02-12

### Fixed

- Replace invalid tool names in agent frontmatter — `MultiEdit` → `Edit`, `LS` → `Glob`, remove `BashOutput`/`KillBash`, `TodoWrite` → `TaskCreate, TaskUpdate` (80 files)
- Remove template placeholder sections (`[Required inputs]`, `[Expected outputs]`, `[Common Edge Case]`, etc.) from 30 agent files
- Remove broken `@../docs/EPCC_BEST_PRACTICES.md` references from 7 EPCC commands
- Disable broken hook entries referencing non-existent scripts in aeo-epcc-workflow
- Remove broken `PostToolUse`, `SubagentStop`, and `Stop` hooks from aeo-performance (invalid variable expansion, missing scripts)
- Replace `$CLAUDE_PROJECT_DIR` → `${CLAUDE_PLUGIN_ROOT}` in aeo-security and aeo-architecture hooks

### Changed

- Rename `/prd` command to `/epcc-prd` to avoid namespace collision
- Bump aeo-nous plugin version to 0.3.0
- Switch aeo-nous extraction model from `opus` to `claude-sonnet-4-5-20250929`
- Fix `LS` → `Glob` in CLAUDE.md agent frontmatter example

## [0.1.5] - 2026-02-10

### Changed

- **aeo-nous**: Statusline ownership inversion — nous no longer owns the statusline pipeline
- **aeo-nous**: `/nous:setup` now appends a trigger block to the user's own `~/.claude/statusline.sh` instead of generating a wrapper script
- **aeo-nous**: `statusline-example.sh` converted from executable renderer to commented integration reference
- **aeo-nous**: Removed `nous-statusline.sh` wrapper approach; old wrappers are no longer needed

## [0.1.2] - 2026-01-31

### Changed

- **markdown-mermaid skill**: Added dark theme as preferred default for consistent colors across all diagram types
- **markdown-mermaid skill**: Added ELK renderer init directives for complex diagrams with edge crossings
- **markdown-mermaid skill**: Added ASCII-only labels rule (avoid emoji/Unicode)
- **markdown-mermaid skill**: Added no-inline-styling rule (use theme directive instead)
- **markdown-mermaid skill**: Updated TB direction guidance for letter-size PDF output
- **markdown-mermaid skill**: Expanded common fixes table with 4 new entries

## [0.1.1] - 2025-01-31

### Changed

- **markdown-mermaid skill**: Improved trigger-focused description with "Use when:" language
- **markdown-mermaid skill**: Expanded copy-paste examples from 3 to 6 patterns (added architecture subgraphs, state machine, mindmap)
- **markdown-mermaid skill**: Expanded critical rules from 4 to 6 (added quote special chars, node ID gotchas)
- **markdown-mermaid skill**: Expanded common fixes table from 4 to 7 issues with more specific solutions

## [0.1.0] - 2025-01-21

### Added

- Initial release with 16 plugins
- **Development plugins**: aeo-architecture, aeo-code-analysis, aeo-documentation, aeo-troubleshooting, aeo-claude, aeo-deployment, aeo-performance, aeo-epcc-workflow
- **Testing plugins**: aeo-tdd-workflow, aeo-testing, aeo-security
- **Automation plugins**: aeo-n8n, aeo-python
- **Productivity plugins**: aeo-agile-tools, aeo-requirements
- **Design plugins**: aeo-ux-design
- 18 skills for domain knowledge (n8n workflows, Mermaid diagrams, React PWA, etc.)
- 65 agents for autonomous task delegation
- 24 slash commands for direct invocation
- Hook configurations for event automation

### Plugin Highlights

- **aeo-epcc-workflow**: Explore-Plan-Code-Commit methodology with `/epcc-explore`, `/epcc-plan`, `/epcc-code`, `/epcc-commit`
- **aeo-architecture**: System design agents for C4 diagrams, ADRs, and architecture review
- **aeo-n8n**: 7 skills covering expressions, node configuration, validation, and workflow patterns
- **aeo-tdd-workflow**: Red-green-refactor methodology with `/tdd-feature` and `/tdd-bugfix`
- **aeo-documentation**: Diataxis framework implementation (tutorials, how-tos, references, explanations)
