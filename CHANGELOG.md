# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.27] - 2026-04-16

### Changed

- **aeo-claude**: Rewrite `opus-prompting` skill description using the symptom-first framing produced by the skill-creator description-optimization loop (20-query trigger eval, 5 iterations over claude-opus-4-7). New description names concrete artifact paths (CLAUDE.md, SKILL.md, `.claude/commands/*.md`, `.claude/agents/*.md`), lists behavioral symptoms that should trigger (MUST/NEVER stacks, agents firing too often, Claude skipping sections, autonomous tool loops, skills that don't activate), and adds an explicit negative guard for MCP server design / hook scripts / API-SDK questions. Note: loop reported no numeric improvement (both original and iter-2 descriptions scored 3/7 test, 5/13 train) because the failing should-trigger queries lose to more specific sibling skills (`plugin-dev:skill-development`, `plugin-dev:agent-development`, `plugin-dev:command-development`, `claude-md-management:claude-md-improver`) when users phrase requests as "create X from scratch". The iter-2 description is adopted anyway for its clearer structure and explicit negative guard. Iterations 3–5 were invalidated by `claude -p` stdout being polluted with harness hook JSON — future runs should use `env -u CLAUDECODE` around the loop invocation (v0.4.27)

## [0.4.26] - 2026-04-16

### Changed

- **aeo-claude**: Follow-up fixes to `opus-prompting` skill after trigger eval — (1) rewrote the skill description to drop the self-contradictory "Covers X, Y, Z" phrasing the skill itself warns against, (2) removed "4 effort levels" from the Think Variants section of `patterns.md`, (3) replaced the enumerated effort-level table in `agentic-patterns.md` with version-agnostic prose. All changes remain free of model numbers, literal context sizes, and enumerated effort-level names. Validated by an iteration-1 skill-creator eval loop across three test cases (CLAUDE.md aggressive language, agent overtriggering, slash command template): fixed skill 21/21 (100%), old snapshot 19/21 (90.5%), no regressions (v0.4.26)

## [0.4.25] - 2026-04-16

### Added

- **aeo-claude**: Add `/aeo-continuation-prompt` command — generates a paste-ready continuation prompt that captures current task state so a fresh session after `/clear` can resume without losing the thread. Useful when a session has accumulated low-value context (dead-ends, tool output) and a clean restart is cheaper than carrying history forward. Accepts an optional focus argument to scope the prompt to a specific thread (v0.4.25)

### Changed

- **aeo-claude**: Refresh `opus-prompting` skill to reflect current Opus model behaviors — describe adaptive thinking without prescribing a specific number of effort levels, note that manual thinking budgets and sampling parameters (temperature, top-p, top-k) are unsupported, add guidance that response length calibrates to task complexity and that autonomous tool loops / subagent spawning are reduced by default. Version-agnostic throughout — no model numbers, no literal context sizes — so guidance remains applicable as models evolve (v0.4.25)

## [0.4.24] - 2026-04-16

### Changed

- **aeo-claude**: Remove `model: opus` frontmatter from `ultrareview`, `ultrareview-fix`, and `ultrareview-loop` skill-commands — the bare `opus` alias is not documented to preserve the caller's model variant, so pinning it risked resolving to the default 200K Opus when invoked from an Opus 4.7 1M session, causing immediate context-window failures for reviews of large plans/codebases. Dropping the field lets these commands inherit the caller's exact model ID (v0.4.24)
- **aeo-nous**: Remove `model: opus` frontmatter from `/aeo-reconcile` command — same rationale as above; reconciliation over large nous stores benefits from the caller's 1M variant when that's what they're running (v0.4.9)

### Fixed

- **aeo-nous**: Reduce SessionStart injection from 20 to 10 entries per store — previous output (~45 KB stdout) exceeded the harness inline cap and was silently truncated, so Claude only received a 2 KB preview of the injected context. Halving keeps injection under the cap while preserving the freshest entries (v0.4.8, backfilled changelog)

## [0.4.23] - 2026-04-15

### Changed

- **aeo-claude**: Scrub `cowork-migrate` skill of user-specific identifiers — replace personal machine-name trigger example (`xps to aurora` → `my laptop to my desktop`), remove SSH-wrapper reference (`tssh`), genericize folder examples (`Downloads\dls`, `OneDrive\temp-from-vault`) to neutral paths (`Documents\work`, `OneDrive\shared-folder`), and change VM_NAME placeholder in `rewrite-paths.py` to explicit `PLACEHOLDER-VM-NAME`. Docs-only changes; no behavior change.

## [0.4.22] - 2026-04-15

### Added

- **aeo-claude**: Add `cowork-migrate` skill — end-to-end procedure for migrating a Claude Cowork session between Windows machines, including sidecar/JSONL extraction, VM VHDX mounting, path rewrites, and the undocumented two-layer compact_boundary truncation workaround. Bundles `stitch-boundaries.py` (with duplicate-UUID handling), `chain-walker.py` (validator), `rewrite-paths.py` (path rewrite template), and `references/truncation-filter.md` documenting Cowork's `cDn`/`sDn`/`iDn`/`lDn` functions reverse-engineered from `app.asar`. Validated against live migrations across two iterations covering five Cowork sessions including a 345 MB / 68-boundary stress case.

## [0.4.21] - 2026-04-13

### Fixed

- **aeo-nous**: Add `--break-system-packages` to pip and `--break-system-packages --system` to uv in pydantic auto-install — fixes PEP 668 externally-managed environment errors on Ubuntu 24.04+ (v0.4.8)

## [0.4.20] - 2026-04-04

### Added

- **aeo-dev**: Add aeo-repo-* governance command family — `aeo-repo-bootstrap`, `aeo-repo-curate-docs`, `aeo-repo-roadmap-alignment-review`, `aeo-repo-sanitize` — ported from OpenAI Codex prompts with Opus-native patterns (v0.3.0)
- **aeo-dev**: Add `repo-governance` skill tying the command family together with purpose, intent, lifecycle guidance, and user-signal-to-command mapping (v0.3.0)

### Changed

- **aeo-claude**: Move aeo-repo-* commands and repo-governance skill from aeo-claude to aeo-dev — repo governance is a developer workflow concern, not a Claude-specific one
- **aeo-claude**: Consolidate skill-creator workspace paths — all ephemeral eval artifacts now go to project-relative `tmp/<skill-name>-workspace/` instead of scattering across skill directories and system `/tmp/` (v0.4.15)
- **aeo-claude**: Add `--results-dir` and `--report` flags to skill-creator description optimization run_loop guidance with `$(pwd)/tmp/` paths for WSL browser interop (v0.4.15)
- **aeo-claude**: Add e2e-only testing policy to ultrareview skills (v0.4.13)
- **aeo-claude**: Standardize `name:` and `version:` frontmatter across all aeo-claude commands (v0.4.14)

### Fixed

- **aeo-claude**: Fix eval_review.html `addRow` focusing wrong textarea after sort — use `data-new` attribute to track and focus the actual new row (v0.4.15)
- **aeo-claude**: Fix eval_review.html textarea using `onchange` (blur-only) instead of `oninput` — summary count now updates as user types (v0.4.15)
- **aeo-claude**: Fix eval_review.html export filename always `eval_set.json` — now includes sanitized skill name (v0.4.15)
- Normalize CRLF→LF line endings in `analyze-prompt.py`
- Add `tmp/` to `.gitignore` for ephemeral eval workspace artifacts

## [0.4.19] - 2026-03-24

### Added

- **aeo-claude**: Add `/aeo-create-claude-prompt` command — guided prompt creation for agentic execution contexts with delivery format routing, token contract validation, output strictness checks, and opus-prompting self-review (v0.4.11)
- **aeo-claude**: Add `/aeo-review-claude-prompt` command — evaluate existing prompts through 7 anti-pattern lenses (content embedding, procedural prescription, exhaustive enums, aggressive language, output clarity, context boundaries, self-defeating instructions) and produce revised versions (v0.4.11)

### Changed

- **aeo-claude**: Refine prompt engineering commands — rewrite `<prep>` to use intent-based guidance instead of prescribing subagent spawns, remove project-specific `run_claude()` references, add `disable-model-invocation: true` to both commands (v0.4.12)
- **aeo-claude**: Add stale-context warning to ultrareview and ultrareview-fix — re-read files from disk before validating, since conversation context may be outdated (v0.4.12)

### Fixed

- **aeo-vsc-cc-sessions-sidecar**: Fix idle_prompt notification to settle as `state: 'idle'` instead of durable blocking prompt — preserves active permission/input prompts when idle hint arrives (v0.3.1)
- **aeo-vsc-cc-sessions-sidecar**: Extract state constants, attention kind constants, and `_set_interaction()` helper — derives `needs_user_attention` from state + attention_kind instead of tracking it redundantly across 8 branches (v0.3.1)

## [0.4.18] - 2026-03-22

### Added

- **aeo-vsc-cc-sessions-sidecar**: Add StopFailure hook — surfaces API errors (rate_limit, auth_failed, billing_error) as `state: 'error'` with raw error type in tool_summary (v0.3.0)
- **aeo-vsc-cc-sessions-sidecar**: Add SubagentStart hook with `subagents` state object — tracks active_count, last_started_type, last_started_at, last_stopped_type; counter resets on SessionStart/SessionEnd (v0.3.0)

### Fixed

- **aeo-vsc-cc-sessions-sidecar**: Fix Stop event to transition state to idle — previously a no-op, leaving sessions stuck in 'thinking' after Claude finishes responding. Guards against overwriting stronger states (error, ended, prompt) (v0.3.0)

### Changed

- **aeo-vsc-cc-sessions-sidecar**: Bump schema_version to 2 and extend self-test to cover Stop→idle, Stop guard states, StopFailure, and SubagentStart/SubagentStop counter logic (v0.3.0)
- **aeo-vsc-cc-sessions-sidecar**: Remove standalone `aeo-vsc-cc-sessions-marketplace` — sidecar is a plugin of `aeo-skill-marketplace` only, not a separate marketplace

## [0.4.17] - 2026-03-22

### Added

- **aeo-vsc-cc-sessions-sidecar**: Add hook sidecar plugin for the AEO VSC CC Sessions VSIX — provides per-process session state, event logging, and lineage via 14 hook events (v0.2.0)
- **aeo-claude**: Add freshness verification step to `/aeo-retro` — re-reads target files and checks for existing coverage before proposing additions (v0.4.10)

### Fixed

- **aeo-claude**: Replace false "safe eval" claim with security warning in Agent SDK calculator example (v0.4.10)
- **aeo-claude**: Refine `/aeo-repo-sanitize` scan categories — clarify git author leak scope, replace "silent code execution" with "untrusted code execution", add methodology-based viability gate questions, fix calibration examples for standard dependency management (v0.4.10)
- **aeo-claude**: Fix `generate_review.py` to recurse into output subdirectories and escape `</script>` in embedded JSON (v0.4.10)
- **aeo-nous**: Pin pydantic dependency to `>=2.0,<3.0` in auto-install and PEP 723 metadata (v0.4.7)

### Changed

- Add defensive `.gitignore` patterns for secrets and credentials (`.env*`, `*.key`, `*.pem`, `credentials*`, `secrets*`)

## [0.4.16] - 2026-03-20

### Added

- **aeo-claude**: Add `/aeo-repo-sanitize` command — scans repo for security risks, PII, secrets, local environment leaks, and supply chain issues before public push. Supports `--auto-approve` flag for automatic remediation (v0.4.9)

## [0.4.15] - 2026-03-15

### Added

- **aeo-dev**: Add plugin with two VS Code extension development skills
  - `vscode-insiders-extension` — targets code-insiders on WSL with verified CSP pitfall resolutions, dual TreeView+WebviewView toggle patterns, and profile-based extension registration fixes
  - `vscode-extension` — generic stable VS Code variant with the same API patterns and CSP guidance
- **aeo-dev**: Document three deployment environments (native, WSL Remote, SSH Remote) with verified directory paths for extensions, profiles, settings, and keybindings
- **aeo-dev**: Add WSL-accessible `/mnt/c/` paths alongside Windows env var paths
- **aeo-dev**: Document that VSIX packages work on both stable and Insiders
- **aeo-dev**: Register plugin in marketplace

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
