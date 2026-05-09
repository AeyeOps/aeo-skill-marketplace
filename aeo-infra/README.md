# aeo-infra

Infrastructure operations skills for Claude Code — AWS CLI v2, Azure CLI, Lima (Linux VMs on Apple Silicon Macs), and MLX/oMLX local LLM serving on Apple Silicon.

## Skills

### aws-cli-operations

AWS CLI v2 expert covering cloud operations, resource management, and automation scripting.

**Trigger phrases:** "aws cli", "run aws command", "aws s3", "aws ec2", "assume role", "cross-account", "JMESPath query", "aws credentials", "aws sso", "aws login", "describe instances", "aws waiter", "create vpc", "lambda deploy", "dynamodb query"

**What it covers:**
- Pre-flight safety checks (identity and region verification)
- Authentication hierarchy: `aws login` (v2.32.0+), SSO, IAM Roles Anywhere, instance roles
- JMESPath queries and server-side filtering
- Pagination, waiters, output formatting, and exit codes
- Credential chain, cross-account patterns, and credential export
- S3 transfer optimization (CRT client, `--no-overwrite`, `--case-conflict`)
- Service patterns: VPC, Lambda, DynamoDB, RDS, CloudWatch, SSM, Security Groups
- Dangerous command awareness and safe alternatives
- v1-to-v2 migration (`aws-cli-migrate` tool)
- Scripting best practices

### az-cli-operations

Azure CLI expert covering cloud operations, resource management, and automation scripting.

**Trigger phrases:** "az cli", "azure cli", "az login", "az account", "service principal", "managed identity", "az vm", "az storage", "az aks", "az keyvault", "az webapp", "az rest", "az graph query", "az bicep", "az role assignment", "cost management", "resource locks"

**What it covers:**
- Pre-flight safety checks (subscription and identity verification)
- Authentication: interactive, device code, managed identity, service principal, federated credentials (OIDC)
- JMESPath queries and output formatting
- `az wait` patterns and parallel operations
- `az rest` for direct REST API calls and cost management queries
- `az graph` (KQL) for cross-subscription resource inventory
- Service patterns: VMs, Storage, VNets/NSGs, Key Vault, App Service, AKS, RBAC
- Dangerous command awareness with tiered risk levels and safer alternatives
- `az bicep` commands and deployment what-if
- Multi-subscription loops and scripting best practices

### lima-vm-operations

Lima 2.x expert for Apple Silicon Macs — install, configure, run, and troubleshoot Linux VMs via Apple's Virtualization.framework (vz).

**Trigger phrases:** "lima", "limactl", "lima.yaml", "lima start", "lima shell", "creating a Linux VM on Mac", "running Linux on Apple Silicon", "Apple Silicon VM", "lima vmType vz", "host.lima.internal", "socket_vmnet", "lima networking", "lima shared/bridged network", "virtiofs mount", "lima port forward", "lima mount writable", "limactl edit", "limactl validate", "limactl template", "lima Rosetta", "running x86 in lima", "lima debug startup"

**What it covers:**
- Pre-flight host checks (arch, macOS version, in-guest username remapping for dotted/uppercase macOS names)
- Installation: `brew install lima`, optional `lima-additional-guestagents` for cross-arch guests, optional `socket_vmnet` for shared/bridged/host networking
- VM lifecycle: `limactl start/stop/list/shell/edit/delete/validate/factory-reset`
- Configuring `lima.yaml`: `vmType: vz`, dual-arch `images:` blocks, virtiofs writable mounts, `mountType` (top-level only), `provision.mode` table, port forwards, `rosetta:`, `containerd:`
- Networking modes table: user-mode default, vzNAT, socket_vmnet shared/bridged/host — when to choose each
- `host.lima.internal` for guest→host reach (resolves via both `/etc/hosts` and Lima's hostResolver)
- Auto-port-forward semantics (1–3s latency, deny-list of sshd `:22` and systemd-resolved `127.0.0.53/54:53`, `hostIP` defaults to `127.0.0.1`)
- A robust group-membership pattern for provisioned users (filters by `/home/` + interactive shell, not by UID — UID-based filters break on macOS-mirrored UIDs and Ubuntu daemon ranges)
- Troubleshooting: read `limactl start` stdout before tailing logs (pre-launch failures don't reach `ha.stderr.log`); `limactl validate` is schema-only; cloud-init heavy provisioning timeout vs actual failure
- Common gotchas: `vmType` is immutable post-create, `template:<name>` syntax (Lima 2.0+), `limactl factory-reset` is all-VMs, SSH ControlMaster caches stale group memberships immediately after provision

**Scope:** v0.5.x targets Apple Silicon (`arm64`) Macs running macOS 13+. Lima on Intel Macs / Linux and Colima are out of scope.

**Companion slash commands** (added in v0.5.0 — agentic springboards, no deterministic wrappers around `limactl`):

- **`/lima`** — menu/intro. Asks the skill what it covers and offers a 4–6 item list of common starting tasks. Useful when a user has heard of Lima but doesn't know where to start. No arguments.
- **`/lima-doctor`** — read-only diagnostic. Runs the skill's Pre-Flight checks plus `limactl list` and reports host fitness, install state, username-remap status, current VMs, and up to 3 tailored next-action recommendations. Proposes mutations rather than performing them.

### mlx-serving

Apple Silicon LLM serving expert covering mlx-lm and oMLX — diagnosing model load failures, OOM, batch>1 crashes, tool-call parsing issues, throughput regressions, and per-model feature-flag tuning.

**Trigger phrases:** "MLX serving", "mlx_lm.server", "oMLX", "Apple Silicon LLM serving", "local LLM on Mac", "model fails to load", "OOM during inference", "batch>1 crash", "tool calls returning as plaintext", "max-concurrent-requests", "turboquant_kv", "dflash", "MTP", "specprefill", "thinking_budget", "OptiQ proxy", "Llama-4 ChunkedKVCache", "Llama-3 tool-call format", "mlx-lm vs oMLX"

**What it covers:**
- Pre-flight environment verification (hardware, MLX core version, mlx-lm version, oMLX subcommands)
- Backend decision matrix: mlx-lm vs oMLX (install, config surface, tool calling, models > RAM)
- Symptom triage: OOM at load vs inference, batch>1 crashes (ChunkedKVCache pattern), tool calls returning as plaintext, throughput regressions, server-log triage
- Server-level oMLX flags from `omlx serve --help`: `--max-concurrent-requests` (default 8), cache controls (`--paged-ssd-cache-*`, `--hot-cache-max-size`, `--no-cache`, `--initial-cache-blocks`), memory ceilings, model-dir
- Per-model `model_settings.json` keys (observed schema; verify per oMLX version): `turboquant_kv_*`, `dflash_*`, `mtp_enabled`, `specprefill_enabled`, `enable_thinking`, `thinking_budget_enabled`, `force_sampling`
- OptiQ proxy concept for models exceeding unified memory
- Bench-it-don't-guess methodology: backend-agnostic harness shape (`--base-url`), suite design (chat / coding / tool_call / tok/s), change attribution, regression detection
- Upstream bug patterns: architecture-specific cache-shape mismatch under batched scheduling; model-family tool-call format not parsed by server — recognize, work around, and report

**Scope:** Apple Silicon (M-series) only. Cloud LLM hosting (Bedrock, OpenAI API, Anthropic API), non-MLX backends (llama.cpp, Ollama, vLLM), and model training are out of scope.

## Installation

```bash
# From marketplace
/plugin install aeo-infra@aeo-skill-marketplace

# Direct
/plugin install ./aeo-infra
```
