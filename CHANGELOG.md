# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.14] - 2026-03-15

### Changed

- **aeo-nous**: Lower context thresholds for 1M context window — `CONTEXT_SKIP_PCT` 10→5 (~50K at 1M), `CONTEXT_EXTRACT_MAX_PCT` 80→60, stop guard `THRESHOLD` 80→65. Aligns extraction and guard firing with research-backed optimal rotation point before context quality degrades (v0.4.7)

## [0.4.13] - 2026-03-09

### Changed

- **aeo-nous**: Add `PRUNE_ROUTES` constant to nous.py and serialize it alongside `WEIGHT_RUBRIC` into reconciliation agent prompts via a "Resolve constants" step in aeo-reconcile.md (v0.4.6)
- **aeo-nous**: Check weight before prune routing in `reconcile_nous_entries()` — entries below discard threshold go to `.discarded.jsonl` regardless of `_prune` tag
- **aeo-nous**: Rename `lens_bleed` to `lens_misclassified` throughout reconciliation prompts and sweep logic
- **aeo-nous**: Simplify misclassification flow — route to `.misclassified.jsonl` by tag instead of lift-and-shift between stores

### Removed

- **aeo-nous**: Remove `get_weight_rubric()` and `get_prune_routes()` accessors — `WEIGHT_RUBRIC` and `PRUNE_ROUTES` are direct module-level imports

## [0.4.12] - 2026-03-08

### Fixed

- **aeo-nous**: Replace broken `CLAUDECODE` absence guard with `agent_id`/`agent_type` provenance check — `CLAUDECODE` env var is not passed to hook subprocesses, so the absence check blocked all hook invocations; new guard correctly skips only subagents, team leads, and `--agent` sessions (v0.4.5)
- **aeo-claude**: Reduce false positives in explore-before-create PreToolUse prompt hook — remove dead `MultiEdit` matcher, front-load JSON response format, reference `cwd` from hook input for project boundary detection, collapse allowlist to 3 verifiable conditions, add motivation clause, and remove unverifiable conditions that the Haiku judge cannot check from `$ARGUMENTS` alone (v0.4.8)

## [0.4.11] - 2026-03-08

### Added

- **aeo-claude**: Add WSL browser compatibility to skill-creator — `browser_open_path()` converts Linux paths to Windows UNC paths via `wslpath` when a Windows-side browser is detected (v0.4.7)
- Add `docs/kb/claude-p-subprocess-patterns.md` knowledge base documenting SDK-to-CLI parity mapping, stream-json parsing, session continuation, and thinking block extraction

### Changed

- **aeo-claude**: Refactor `generate_review.py` metadata and grading lookup into `_find_json_in_ancestors()` that walks up the directory tree instead of checking only two fixed locations
- **aeo-claude**: Use `python3 -m webbrowser` instead of `open` for cross-platform browser launching in skill-creator SKILL.md

## [0.4.10] - 2026-03-07

### Changed

- **aeo-nous**: Replace bespoke `NOUS_SUBPROCESS` env var with `CLAUDECODE` absence check for subprocess detection — `claude --print` does not re-set `CLAUDECODE` in child process, so stripping it is sufficient to suppress hooks in subprocesses (v0.4.4)
- **aeo-claude**: Remove `NOUS_SUBPROCESS` from skill-creator subprocess env setup — CLAUDECODE stripping already provides the signal (v0.4.6)

### Removed

- **aeo-nous**: Remove `hook-profiler.sh` and all profiler-only hook event registrations (SessionEnd, PreCompact, SubagentStop, Notification, UserPromptSubmit)
- **aeo-nous**: Remove dead `NOUS_SESSION` and `NOUS_PROJECT` env vars from extraction subprocess spawning

## [0.4.9] - 2026-03-06

### Fixed

- **aeo-claude**: Fix skill-creator eval producing 0% recall — create temp skills in `.claude/skills/` instead of `.claude/commands/` so they appear in the skills list, fix multi-turn stream detection that was preventing parallel description optimizations, and allow `ToolSearch` as a pass-through for deferred tool loading

## [0.4.8] - 2026-03-05

### Added

- **aeo-claude**: Add patched skill-creator fork with full subscription compatibility — replace Anthropic SDK calls with `claude -p` subprocess pattern in `improve_description.py` and `run_eval.py` so all features work with CLI authentication instead of requiring a separate API key (v0.4.5)

### Changed

- **aeo-nous**: Raise stop-guard block threshold from 65% to 80% context usage (v0.4.3)
- **aeo-nous**: Raise extraction ceiling from 60% to 70% context usage
- **aeo-nous**: Add thin-window skip — suppress extraction when transcript window has fewer than 20 lines since last checkpoint
- **aeo-nous**: Restructure weight rubric bands with explicit verification requirements per band and w_at freshness integrity rules
- **aeo-nous**: Improve aeo-reconcile command with plugin path resolution, verification ledger, jq recipes, lift-and-shift lens bleed handling, and cross-cursor dedup checks

### Fixed

- **aeo-nous**: Filter null-context statusline entries in nous-logger.sh before writing to activity JSONL — eliminates ValidationError warnings when nous.py reads entries emitted during session startup

## [0.4.7] - 2026-03-04

### Added

- **aeo-nous**: Add `/aeo-reconcile` slash command for curating nous stores — prunes stale entries, resolves conflicts, deduplicates, and handles cross-store lens bleed (v0.4.2)
- **aeo-nous**: Add `flush_inbox.sh` and `reconcile_nous_entries.sh` scripts for command-driven reconciliation
- **aeo-nous**: Add `reconcile_nous_entries()` function and `WEIGHT_RUBRIC` to nous.py for weighted entry management and deterministic sweep

### Changed

- **aeo-nous**: Pass paths via env vars in shell scripts instead of interpolating into Python string literals (injection fix)
- **aeo-nous**: Add `flush_inbox()` to ExtractionLens base for draining inbox fragments before reconciliation
- **aeo-claude**: Add explore-before-create PreToolUse prompt hook gating new file/function/class creation (v0.4.4)

## [0.4.6] - 2026-03-02

### Added

- **aeo-infra**: Add az-cli-operations skill (v0.3.0) covering Azure CLI authentication, credential chain, JMESPath queries, service patterns (VMs, Storage, VNets, Key Vault, App Service, AKS, RBAC), dangerous command awareness, cost management via `az rest`, and Resource Graph (KQL)
- **aeo-infra**: Add 3 Azure reference modules — dangerous-commands, service-patterns, advanced-patterns

### Changed

- **aeo-claude**: Restore ultrareview source-reading protocol, evidence fields, NEEDS_VALIDATION detail, and artifact inventory sections (v0.4.3)
- **aeo-claude**: Rewrite opus-prompting as artifact-type writing assistant with per-context guidance (CLAUDE.md, skills, commands, agents) and self-check workflow
- **aeo-claude**: Genericize opus-prompting references from model-specific "Opus 4.6" to future-proof "Claude" phrasing, add Prefill row to patterns quick reference
- **aeo-claude**: Add `--approve-all` flag to aeo-retro command for automated pipeline usage
- Update marketplace.json with Azure CLI tags and description for aeo-infra

## [0.4.5] - 2026-02-24

### Added

- **aeo-claude**: Add `/aeo-retro` session retrospective command — extracts durable insights from session transcripts, reconciles stale guidance in CLAUDE.md/SKILL.md files and nous entries, routes findings to appropriate destinations with user approval

### Fixed

- **aeo-claude**: Remove stray blank line in ultrareview-loop `loop-hook.sh`

## [0.4.4] - 2026-02-17

### Added

- **aeo-infra**: Add AWS infrastructure operations plugin (v0.2.0) with aws-cli-operations skill covering CLI v2 authentication, credential management, JMESPath queries, service patterns (VPC, Lambda, DynamoDB, RDS, CloudWatch, SSM), dangerous command awareness, and S3 transfer optimization
- **aeo-infra**: Add 3 reference modules — dangerous-commands, service-patterns, advanced-patterns

### Changed

- **CLAUDE.md**: Rewrite project documentation with validation commands, loading instructions, hook exit code semantics, `${CLAUDE_PLUGIN_ROOT}` usage, key subsystems (Nous, Ultrareview-loop, EPCC), cross-cutting architecture patterns, and contributing guide
- Update marketplace.json with aeo-infra plugin entry and infrastructure category

## [0.4.3] - 2026-02-17

### Changed

- **aeo-nous**: Move Stop hook context blocking to dedicated sync guard script (`nous-stop-guard.sh`)
- **aeo-nous**: Make `nous.py` Stop hook async to avoid blocking UI during extraction
- **aeo-nous**: Modernize typing (`Optional[X]` → `X | None`), remove unused `multiprocessing` import
- **aeo-nous**: Filter `CLAUDECODE` env var from subprocess spawning to prevent hook recursion

### Added

- **aeo-nous**: Add `nous-stop-guard.sh` — fast sync guard that checks context >65% and emits block decision

## [0.4.2] - 2026-02-13

### Changed

- Bump 14 plugin versions from 0.2.0 to 0.3.0 to reflect v0.3.0–v0.4.0 work (deduplication, new skills/commands, restructuring)
- Bump aeo-nous from 0.3.0 to 0.4.0 to reflect post-sync changes

### Removed

- Remove docs/issues/ audit tracking files (all issues resolved)

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
