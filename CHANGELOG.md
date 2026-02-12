# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
