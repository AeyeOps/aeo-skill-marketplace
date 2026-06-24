# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.51] - 2026-06-24

### Added

- **aeo-claude**: Add shared Cowork storage and bundle utilities for future export/import workflows, with generated bundle and local Cowork state artifacts excluded from version control. Plugin internal version 0.4.32 → 0.4.33.

### Changed

- **aeo-claude**: Document plugin-level shared resources in `skill-creator`, so future skills can reference shared plugin files with `${CLAUDE_PLUGIN_ROOT}` instead of copying shared contracts into each skill.

## [0.4.50] - 2026-05-23

### Added

- **aeo-infra**: new `tailscale-macos-headscale` skill (plugin 0.6.6 → 0.6.7) covering Tailscale.app installation via Homebrew Cask, the NetworkExtension permission grants on macOS Tahoe, recovery from a conflicting brew formula install, `tailscale up --login-server` against a self-hosted headscale, the deep-link `tailscale://changelogin` fallback when the CLI cannot reach the daemon, the `headscale preauthkeys create --user <numeric-id>` gotcha, and verification commands. Three files: SKILL.md + installing-tailscale-on-macos.md + joining-headscale-from-macos.md.

## [0.4.49] - 2026-05-23

### Changed

- **aeo-infra**: `glinet-slate7` `wireguard-server-api.md` (plugin 0.6.5 → 0.6.6) updated to reflect actual `wg-server` RPC behavior — `set_peer` ignores `public_key`/`private_key`; `generate_peer` doesn't rotate; UCI and kernel state can diverge. Added a *Rotating an existing peer's keypair* section with the surgical `uci set` + `wg set` flow, and a PSK base64-padding pitfall.

## [0.4.48] - 2026-05-10

### Changed

- **aeo-infra**: `glinet-slate7` SKILL.md (plugin 0.6.4 → 0.6.5) — reference-files row for `wg-client-stacked-tunnels.md` reframed for progressive disclosure: leads with explicit **Read when:** triggers (configuring a Linux WG client against the GL-iNet server, debugging a full-tunnel WG client that won't reach the internet or tailnet, layering Tailscale/ZeroTier/another overlay on top of a WG client, or diagnosing symptoms like *`tailscale ping --tsmp` works but ICMP/SSH to a tailnet peer doesn't*, *`tailscale netcheck` reports UDP blocked*, or *large transfers stall while small probes succeed*) followed by **Contents:** describing what's inside, so an agent can decide whether to load the file before reading it. Also: the [0.4.46] and [0.4.47] release commits were rewritten in trunk to remove the `Co-Authored-By: Claude` trailer per the marketplace's no-attribution convention; anyone who pulled before this force-push will see a divergent local history and should reset to the new trunk hashes (v0.4.48)

## [0.4.47] - 2026-05-10

### Added

- **aeo-infra**: `glinet-slate7` skill gains a third new reference file, `wg-client-stacked-tunnels.md`, covering the Linux client side of a WireGuard link to a GL-iNet sdk4 server and how to layer an overlay VPN (Tailscale, ZeroTier) on top without leaking. Documents `wg-quick`'s policy-routing internals for full-tunnel `AllowedIPs` (table 51820, fwmark `0xca6c`, rules at 5208 with `suppress_prefixlength 0` and 5209 catch-all), MTU selection rules-of-thumb for stacked tunnels (single layer, Wi-Fi to GL-iNet, NAT'd guest network, overlay-on-WG), and the two leak modes that appear when Tailscale is added on top: (1) Tailscale's `fwmark 0x80000/0xff0000` rules at priorities 5210/5230/5250 bypass the wg-quick default route to the underlying NIC; the fix is a higher-priority rule at 5200 that captures the same fwmark and sends it into table 51820 (so DERP fallback rides wg0 instead of leaking); (2) wg-quick's catch-all at 5209 shadows Tailscale's per-peer `/32` routes in table 52, so ICMP/TCP to mesh peers fail while only TSMP works; the fix is destination-based rules at 5205/5206 that send `100.64.0.0/10`, `100.100.100.100/32`, and the IPv6 ULA `fd7a:115c:a1e0::/48` to table 52 before 5209 fires. Includes a copy-pasteable `wg0.conf` `PostUp`/`PreDown` block, the final ip-rule layout for a working Tailscale-over-WG stack, a leak-verification recipe (tcpdump filter that captures only legitimate management plane traffic; anything else is a leak), and a diagnostic command table covering `ip route get … mark <fwmark>`, `ss -tunpe`, `tailscale ping --tsmp`, `tailscale ping --until-direct=false`, `tailscale netcheck`, and journalctl interpretation. Closes with a generalization to other overlay VPNs (ZeroTier, Nebula, OpenVPN) and a 5-step approach for any overlay-on-WG stack. SKILL.md frontmatter description widened, reference-files table extended, and a new common-task entry added ("Layer Tailscale (or another overlay VPN) on top of a WG client tunnel"). Plugin internal version 0.6.3 → 0.6.4 (v0.4.47)

## [0.4.46] - 2026-05-10

### Added

- **aeo-infra**: `glinet-slate7` skill expanded with two new reference files covering the GL-iNet sdk4 admin-panel API surface — applicable across most GL-iNet sdk4 firmware devices, not only the Slate 7. `json-rpc-api.md` documents the `/rpc` JSON-RPC 2.0 backend: endpoint and transport, the challenge → SHA-256 crypt → sid auth flow (with an `openssl passwd -5` example since `crypt` was removed in Python 3.13), the `call` envelope shape, error code conventions (`-32000` Access denied, `-32602` Invalid params, application-level `err_code` returned inside `result`), module discovery via `/usr/lib/oui-httpd/rpc/` listing, method discovery via `.so` `strings` and gzipped Vue bundles in `/www/views/`, a common modules table (`wg-server`, `wg-client`, `ovpn-*`, `tailscale`, `system`, etc.), a reusable bash helper with sid caching and one-shot retry on session expiry, and pitfalls (empty-string fields rejected, JSON number vs string types, nginx-fronted 500s, silent session timeouts). `wireguard-server-api.md` is a deep dive on the `wg-server` module: full method table with parameter shapes and return types, `add_peer` accepted fields with validation rules, `generate_peer` response field-naming convention (from the *client's* perspective — `private_key` is the client's private key, `public_key` is the server's public key for the client's `[Peer]` block), end-to-end provisioning flow (`set_setting` → `add_peer` → `generate_peer` → `start`), server-side state inspection cross-checks (UCI vs kernel `wg show` vs RPC `get_status`), settings semantics (`client_to_client`, `masq`, `local_access`), the local-only `Endpoint = <LAN-IP>:<port>` pattern for LAN-side clients with no DDNS or upstream port-forwarding required, a tcpdump-based leak-verification recipe, and pitfalls (first-peer-add regenerates server keys, `wgserver` interface name vs client-side `wg0`, `mtu: 0` defaulting to 1420 vs explicit 1280 for tunnel-in-tunnel paths, destructive re-`generate_peer` after handing out a config). `SKILL.md` updated: frontmatter description widened to mention the JSON-RPC API and wg-server module surface; reference-files table extended with both new entries; three new common-task shortcuts ("Provision WireGuard server programmatically", "Script the admin panel", "Build a LAN-only WireGuard tunnel"). Plugin internal version 0.6.2 → 0.6.3 (v0.4.46)

## [0.4.45] - 2026-05-10

### Changed

- **aeo-dev**: `aeo-repo-sanitize` command (v0.4.0 → v0.4.3) — four improvements: (1) default scan scope tightened to git-tracked and staged-new files only; `--include-untracked` flag added for pre-`git add -A` scans that need to catch issues in new files before they enter the index; (2) new Category 4 (Documentation & Skill Content) covers `.md` and prose files for real absolute paths with machine-specific usernames, internal hostnames/FQDNs, private-range IPs beyond product-default values, non-public URLs, environment-specific config values, real usernames in SSH/path examples, hardware fingerprinting (specific chip models, exact RAM/GPU identifiers that identify a rig), internal service/agent names in shipped docs, and changelog oversharing of internal details; (3) calibration examples added to distinguish generic tier descriptions from rig-specific identifiers (chip model names, exact RAM amounts, GPU identifier strings); (4) parallel agent count updated from 3 to 4. Plugin internal version 0.3.0 → 0.3.1 (v0.4.45)

## [0.4.44] - 2026-05-10

### Added

- **aeo-infra**: New `glinet-slate7` skill (v1.0.0) — comprehensive reference for the GL-iNet Slate 7 (GL-BE3600) Wi-Fi 7 travel router. Four-file progressive-disclosure structure: `SKILL.md` (quick reference table, capabilities summary, common tasks, network modes comparison) plus `hardware-and-features.md` (specs, ports, touchscreen interface, Wi-Fi 7/MLO, all software features with interaction constraints, network modes), `web-ui-guide.md` (full admin panel menu structure, WireGuard/OpenVPN client flows for 30+ providers, VPN server setup with client profile export, AdGuard Home, DDNS, Tailscale, Multi-WAN), `setup-and-management.md` (initial connection, first-time wizard, SSH/CLI with command reference, touchscreen-guided reset (Repair Mode vs Reset Mode), factory reset, firmware update, U-Boot recovery). Plugin internal version 0.4.32 → 0.4.33; marketplace.json description and tags updated (v0.4.44)

## [0.4.43] - 2026-05-09

### Changed

- **aeo-infra**: `lima-vm-operations` skill (v0.5.1 → v0.5.2) refactored to a progressive-disclosure layout — the single `SKILL.md` is now a short dispatcher (scope, pre-flight, core principles, networking decision shortcuts, pointers) with deep content moved into seven on-demand reference files under `references/`: `installation.md`, `lifecycle.md`, `lima-yaml.md`, `networking.md`, `mounts.md`, `workflows.md`, `troubleshooting.md`. SKILL.md links each reference at least once and references cross-link only where context bridges them — DRY, no duplication, no orphans. Companion slash commands `/lima` and `/lima-doctor` updated to address the skill by plugin-qualified form `aeo-infra:lima-vm-operations` rather than by `${CLAUDE_PLUGIN_ROOT}` file path, matching the cross-coupling convention from v0.4.35. Personal/environment-specific tokens scrubbed from the skill content for marketplace publication. Plugin internal version 0.6.0 → 0.6.1 (v0.4.43)

## [0.4.42] - 2026-05-09

### Added

- **aeo-infra**: New `mlx-serving` skill (v1.0.0) — Apple Silicon LLM serving expert covering both `mlx-lm` and `oMLX` backends. Five-file progressive-disclosure structure: `SKILL.md` (pre-flight, mlx-lm vs oMLX decision matrix, symptom→cause triage, core principles) plus four references — `symptoms.md` (OOM at load/inference, batch>1 crashes, tool-calls-as-text, throughput regression, server-log triage), `omlx-feature-flags.md` (server-level `omlx serve` flags verified from `--help` plus per-model `model_settings.json` keys), `bench-methodology.md` (backend-agnostic harness shape via `--base-url`, suite design, change attribution, regression detection), `upstream-bug-patterns.md` (architecture-specific cache-shape mismatch under batched scheduling; model-family tool-call format not parsed by server). Source content distilled from a fleet-tuning initiative covering 5 models including Llama-4-Scout, Mistral-Medium-3.5-128B, and three Gemma variants — with two upstream bugs identified and patched (ChunkedKVCache batch=1 in scheduler, Llama-3-style `{"name","parameters"}` JSON tool-call parsing). Skill content scrubbed of all machine-specific tokens (paths, IPs, hostnames, fork PR numbers) for marketplace publication. Plugin internal version 0.5.0 → 0.6.0; description and marketplace.json description updated to mention MLX/oMLX serving alongside AWS/Azure/Lima; keywords expanded with `mlx`, `omlx`, `mlx-lm`, `llm-serving`, `local-llm`, `llama`, `gemma`, `mistral`, `kv-cache`, `turboquant`, `dflash` (v0.4.42)

## [0.4.41] - 2026-05-09

### Added

- **aeo-infra**: `lima-vm-operations` skill (v0.5.0 → v0.5.1) gains an "Opting out of the `lima` remap" subsection in Pre-Flight, written as agent-active guidance: when a user asks to give the in-guest user a custom name instead of the silent `lima` fallback, Claude is told to gather inputs directly from the host (`id -un`, `id -u`, `id -F`) rather than asking the user to look them up, derive a Linux-valid name, confirm the choice, and write `~/.lima/_config/override.yaml` with `user: { name, uid, comment }`. The override applies to newly-created VMs only and is reversible. Plugin internal version unchanged at 0.5.0 (skill-only patch) (v0.4.41)

## [0.4.40] - 2026-05-09

### Added

- **aeo-infra**: Two slash commands for `lima-vm-operations` skill (v0.4.1 → v0.5.0) — agentic springboards designed for first-time discovery, not deterministic wrappers around `limactl`. (1) `/lima` — no-arg menu/intro that summarizes scope (Apple Silicon Mac, Lima 2.x; Intel/Linux/Colima out of scope) and offers 4–6 common starting tasks. (2) `/lima-doctor` — read-only diagnostic that runs the skill's Pre-Flight + `limactl list` and reports host fitness, install state, username-remap status, existing VMs, and up to 3 tailored next-action recommendations. Both command bodies are short (under ~15 lines) and explicitly point at SKILL.md as the source of truth — they don't duplicate the skill's content. SKILL.md's Pre-Flight section now cross-references both commands. Plugin internal version 0.4.0 → 0.5.0; description and marketplace.json description updated to mention the springboards. Why a divergence from the existing aws/az skills (which have no commands): Lima has more "decisions to make at start" than the AWS/Azure CLIs, and a discovery menu meaningfully closes the UX gap for users who don't already know Lima exists (v0.4.40)

## [0.4.39] - 2026-05-09

### Added

- **aeo-infra**: New `lima-vm-operations` skill (v0.4.1) — Lima 2.x expert for Apple Silicon Macs covering install, configuration, VM lifecycle, networking modes (user-mode/vzNAT/socket_vmnet shared/bridged/host), virtiofs mounts, host↔guest reach via `host.lima.internal`, auto-port-forward semantics including the deny-list, troubleshooting startup failures, and a robust group-membership pattern for provisioned users. Apple Silicon scope only for v0.4 — Intel Macs, Lima-on-Linux, and Colima are out of scope. Plugin internal version 0.3.0 → 0.4.0; description updated; keywords expanded with `lima`, `limactl`, `vm`, `virtualization`, `apple-silicon`, `macos`, `linux-vm`, `vz`, `virtiofs` (v0.4.39)

## [0.4.38] - 2026-05-08

### Fixed

- **aeo-deployment**: Fixed silently-broken YAML frontmatter in `agents/deployment-agent.md`. The `description:` field contained `Examples: 'deploy with zero downtime', ...` — the unquoted nested colon made YAML treat `Examples` as a sub-mapping and the parse failed, so at runtime the agent loaded with empty metadata (all frontmatter fields silently dropped, exactly the same class of bug cleaned up in aeo-docs at v0.4.34). Wrapped the value in double quotes and removed a stray blank line inside the frontmatter block. `claude plugin validate` now passes. Plugin internal version 0.3.1 → 0.3.2 (v0.4.38)

## [0.4.37] - 2026-05-08

### Changed (breaking)

- **aeo-deployment**: Slash command `/release-notes` renamed to `/rel-notes` to avoid colliding with Claude Code's built-in `/release-notes`. The collision prevented the built-in from running even when explicitly selected. File renamed `aeo-deployment/commands/release-notes.md` → `rel-notes.md`; frontmatter `name:` and three in-body usage examples updated. Anyone scripting against `/release-notes` from this plugin must migrate to `/rel-notes` (fully-qualified: `/aeo-deployment:rel-notes`). Plugin internal version 0.3.0 → 0.3.1 (v0.4.37)

## [0.4.36] - 2026-05-08

### Changed (breaking)

- **aeo-security**: Plugin internal version bumped 0.3.0 → 0.4.0. Relaxed `hooks/security_check.py validate_file_path()` so it no longer blocks Write/Edit operations on paths outside the primary `CLAUDE_PROJECT_DIR`. The check now only blocks the universally-bad cases (`..` traversal, writes into `/etc /sys /proc /boot /root /bin /sbin /usr/bin /usr/sbin /usr/local/bin /usr/local/sbin`). Why: the previous rule had no awareness of `/add-dir`'d additional working directories, so legitimate multi-repo workflows were blocked with no env-hook to opt in. The credential/secret protections (`is_sensitive_file`, `scan_for_secrets`) are unchanged — those are the real value of the hook (v0.4.36)

## [0.4.35] - 2026-05-08

### Changed

- **aeo-docs**: Sibling-skill cross-references upgraded from bare names (`` `d2` skill in this plugin``) to plugin-qualified form (`aeo-docs:d2`). 11 references across 5 files in the new `diataxis` and `architecture-docs` skills now use `aeo-docs:<skill>` notation. Why: per the marketplace cross-coupling rule, skills should reference each other by `<plugin>:<skill>` so the loader resolves the correct location regardless of cache layout — bare names were ambiguous when two plugins ship a similarly-named skill. Plugin internal version 0.5.0 → 0.5.1 (v0.4.35)

## [0.4.34] - 2026-05-08

### Changed (breaking)

- **aeo-docs**: Plugin internal version bumped 0.4.0 → 0.5.0. Retired all 6 agents (`docs-tutorial-agent`, `docs-howto-agent`, `docs-reference-agent`, `docs-explanation-agent`, `documentation-agent`, `architecture-documenter`) and all 5 slash commands (`/docs-create`, `/docs-tutorial`, `/docs-howto`, `/docs-reference`, `/docs-explanation`) in favor of two new skills. Anyone scripting against `@docs-*-agent` references or invoking `/docs-*` commands will need to migrate (callers can now state the documentation task plainly — the skills detect the activation). The 6 retired agents had silent YAML-frontmatter parse errors anyway (unquoted `Examples: '...'` colons in `description:`), which is part of why nobody noticed they weren't fully wired (v0.4.34)
- **aeo-epcc-workflow**: Two `commands/reference/` files updated to drop `@documentation-agent` references — `code-implementation-patterns.md` and `pattern-recognition.md` now point readers at the new `diataxis` and `architecture-docs` skills. Description string also updated from `aeo-documentation` → `aeo-docs` to match the rename. Plugin internal version 0.3.0 → 0.3.1 (v0.4.34)

### Added

- **aeo-docs**: New `diataxis` skill consolidates the 4 retired Diataxis quadrant agents into a single skill that picks the right mode (tutorial / how-to / reference / explanation) for the request and applies the matching template. Skill body is the decision matrix; per-mode templates live in `references/{tutorial,howto,reference,explanation}.md` and load only when relevant. Trigger-optimized description per opus-prompting guidance (verb-phrase activation, no MUST / NEVER stacks). Replaces ~1,500 lines of duplicated framework prose across the old quadrant agents with a single source of truth (v0.4.34)
- **aeo-docs**: New `architecture-docs` skill replaces the retired `architecture-documenter` agent. Covers C4 model (`references/c4-model.md`), ADRs (`references/adr-template.md`), OpenAPI specs (`references/openapi.md`), and system / component design docs (`references/system-and-component-design.md`). Explicitly scoped — *not* user-facing documentation, that's `diataxis` (v0.4.34)
- **aeo-docs**: Both new skills validated via a 4-eval skill-creator harness (3 diataxis modes + 1 ADR) before commit. Reviewer feedback applied as in-version polish: SKILL.md ↔ reference duplication trimmed, explanation template re-framed as a maximal menu rather than a checklist, reference template gained nested-keys heading guidance and a streamlined env-var section (v0.4.34)

### Fixed

- **aeo-docs**: Eliminated the 6 silently-broken agent frontmatter parse errors that were surfaced (but not fixed) during the 0.4.33 d2 import. The agents are gone; the skill replacements have valid YAML frontmatter (v0.4.34)

## [0.4.33] - 2026-05-08

### Changed

- **aeo-docs** (renamed from `aeo-documentation`): Plugin renamed for brevity; existing installs of `aeo-documentation@aeo-skill-marketplace` will need to reinstall under `aeo-docs@aeo-skill-marketplace`. Plugin internal version bumped 0.3.0 → 0.4.0 to reflect the rename plus the bundled d2 skill (v0.4.33)
- **aeo-epcc-workflow**: Companion-plugin reference updated from `aeo-documentation` to `aeo-docs` to match the rename (v0.4.33)

### Added

- **aeo-docs**: Bundled the Terrastruct `d2` skill (declarative diagramming language for state machines, ER diagrams, sequence diagrams, C4, class diagrams, and more) alongside the existing `markdown-mermaid` skill. The skill ships its own SKILL.md, 16 reference files (grammar cheatsheet, layouts, edge routing, sql/er, sequence, class, grid diagrams, etc.), and 13 example `.d2` files. Activates whenever the user asks for d2 diagrams or describes a diagram type d2 specializes in (v0.4.33)

## [0.4.30] - 2026-04-17

### Changed

- **aeo-nous**: SessionStart inline injection is now byte-budgeted. A new `INJECT_BYTE_BUDGET = 5000` constant caps the total bytes emitted inline across both lenses (split evenly — 2500 per lens), and a new `take_within_budget()` helper selects entries in `effective_score` order, whole-or-not-at-all, stopping on the first entry that would overflow the per-lens cap. The previous count-only limit (unconditional top-10 per lens) could produce 26+ KB of stdout, which the Claude Code harness spilled to a tool-results file and left only a ~2 KB preview in the model's context — so most injected memory was silently invisible. The 10+10 count ceiling is preserved as a hard upper bound; the byte budget is the new soft fence that prevents the harness spill (v0.4.10)

### Added

- **aeo-nous**: SessionStart now writes the full per-project corpus (all engram + cortex entries, sorted by `effective_score`) to `/tmp/nous-session-<session_id>.md` on every startup when `session_id` is available, and emits a new `<nous_spill>` block that cites the absolute path in backticks with conditional-read guidance ("Read this file when an inline entry looks truncated or when the current task might depend on memory below the inline fold"). The model reads the spill on demand rather than paying a Read tax every session. No fallback when `session_id` is empty (hook skips the spill rather than inventing a filename); `/tmp/` lifecycle is left to the OS — transient fit for transient context (v0.4.10)

## [0.4.29] - 2026-04-16

### Fixed

- **aeo-claude**: Prefix the `ultrareview-loop` setup-script invocation with `noglob` so zsh does not expand `$ARGUMENTS` (or any literal glob metacharacters in the user's arguments) before the script sees them. Without it, arguments containing `*`, `?`, or `[` could either match unrelated files in the cwd or abort the hook with "no matches found" under zsh's default `NOMATCH` setting (v0.4.29)

## [0.4.28] - 2026-04-16

### Fixed

- **aeo-claude**: Enforce plan-mode entry in `ultraplan` and `ultraplan-teams` skills. `ultraplan` previously listed `EnterPlanMode` in `allowed-tools` but the body never instructed Claude to call it — the workflow jumped straight to Read/Glob/Grep, so plan mode was silently skipped. `ultraplan-teams` had the instruction but buried at Phase 1 step 1, easy to skip when investigation felt cheaper. Both skills now open with a `<plan-mode-precondition>` XML block right after the H1, add "Call EnterPlanMode first if you are not already in plan mode" to the "Begin Planning" footer, and (for ultraplan) introduce an explicit "### 0. Enter Plan Mode" workflow step. Rationale is inlined — unapproved implementation / overlapping file ownership are named as the failure modes the gate prevents — so Claude can't rationalize skipping. Changes written following opus-prompting guidance: semantic XML over bolded MUST stacks, rationale explained once, idempotent re-entry handled ("If already in plan mode, continue") (v0.4.28)

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
