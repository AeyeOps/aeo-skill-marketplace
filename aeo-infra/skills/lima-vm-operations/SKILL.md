---
name: lima-vm-operations
version: 0.5.2
description: >-
  This skill should be used when the user asks about "Lima", "limactl",
  "lima.yaml", "lima start", "lima shell", "creating a Linux VM on Mac",
  "running Linux on Apple Silicon", "macOS Linux VM", "Apple Silicon VM",
  or wants to "install Lima", "configure a Lima VM", "edit lima config",
  "spin up an Ubuntu VM on my Mac", or "use Lima to run Docker on macOS".
  Also applies for "lima vmType vz", "lima vz vs qemu", "host.lima.internal",
  "socket_vmnet", "lima networking", "lima shared network", "lima bridged
  network", "virtiofs mount", "9p mount", "lima port forward", "lima mount
  writable", "limactl edit", "limactl validate", "limactl template", "lima
  Rosetta", "running x86 in lima", "lima debug startup", or any task involving
  spinning up, configuring, troubleshooting, or shelling into a Lima VM on an
  Apple Silicon Mac. Use this skill whenever Lima is mentioned even if the user
  doesn't explicitly ask for "help" — the right configuration choices (vz vs
  qemu, mount type, network mode) are non-obvious and easy to get wrong.
---

# Lima VM Operations (Apple Silicon)

Guidance for installing, configuring, and running Lima — Linux VMs on macOS — on Apple Silicon Macs.

**Scope:** Lima 2.x on Apple Silicon (`arm64`) Macs running macOS 13 or later. Lima also runs on Intel Macs and Linux, but the defaults, performance, and feature set differ enough that those cases are out of scope here. Colima (a Docker-focused wrapper around Lima) is also out of scope.

**Why a skill:** Lima exposes a lot of knobs. The `vz` vs `qemu` choice, the four networking modes, and the mount-type selection each have consequences that aren't obvious from the help output. Choosing wrong gets you a VM that boots but can't reach the LAN, mounts your code read-only when you needed write, or runs at a fraction of the speed because it picked the wrong hypervisor. Defaults are right *most* of the time on Apple Silicon — this skill says when to deviate and why.

---

## Pre-Flight: Verify the Host

Before doing anything else, confirm the Mac is suitable and check what's already installed:

```bash
uname -m                 # must be arm64 for this skill's guidance
sw_vers                  # ProductVersion must be >= 13 for vz; >= 14 for full virtiofs
limactl --version 2>/dev/null || echo "lima not installed"
brew list --versions socket_vmnet 2>/dev/null || echo "socket_vmnet not installed"
```

If `uname -m` is `x86_64`, this skill's `vmType: vz` recommendations don't apply (vz is Apple-Silicon-only) — fall back to `vmType: qemu`.

For a one-call summary of host fitness, install state, and existing VMs, run **`/lima-doctor`** — it executes this Pre-Flight plus `limactl list` and recommends next actions. The unbounded **`/lima`** command is the menu/springboard for "what does this skill help with?"

**Username gotcha:** Lima derives the in-guest user from your macOS username, but Linux requires the username to match `^[a-z_][a-z0-9_-]*$`. macOS names with dots, uppercase, or other characters (e.g. `Jane.Doe`, `j.smith`) get **silently remapped to `lima`** in the guest. That changes `$HOME`, the SSH user, and which path your `~` mount lands at. Check yours with `id -un` — if it doesn't match the regex, expect to use `lima` (not your Mac username) inside the VM, and write provisioning scripts accordingly. To opt out and keep a custom in-guest username, see `references/lima-yaml.md` (override.yaml section).

A related cosmetic side effect: `limactl shell <name>` tries to `cd` into the host's current working directory inside the guest. If that path isn't mounted, every shell invocation prints a harmless `bash: line 1: cd: <path>: No such file or directory` and lands you in `$HOME` instead. Quiet it with `cd /tmp` first, or pass `--workdir=/` *before* the VM name (the flag must precede the VM name — `limactl shell --workdir=/ <name> <cmd>` works; `limactl shell <name> --workdir / -- <cmd>` fails confusingly).

---

## Core Principles

1. **Default to `vmType: vz`** on Apple Silicon. Apple's Virtualization.framework is faster and supports virtiofs mounts. Fall back to `qemu` only when vz can't satisfy a requirement (older macOS, certain device emulation).
2. **Edit, don't recreate.** `limactl edit <name>` mutates the YAML of an existing VM; recreating to change one field loses VM state. The VM must be stopped to edit most fields.
3. **Validate before starting — but know its limits.** `limactl validate ./my.yaml` catches *schema* errors. It does **not** check arch matches between host and `images:` entries, that URLs resolve, or that mount paths exist — those are runtime concerns surfaced by `limactl start`. Use validate as a cheap typo gate, not a pre-flight green light.
4. **Templates over hand-rolling.** Built-in templates (`template:default`, `template:docker`, `template:k3s`, etc.) encode the right vmType, image, and provisioning for common cases. Start from a template, then `limactl edit` to customize. (Lima 2.0+ uses `template:<name>`; older docs you'll find online still use `template://<name>` — that form is deprecated but still works.)
5. **Mounts are NOT writable by default.** Every mount entry needs `writable: true` if the guest needs to write — silent read-only mounts are a top source of "why is `npm install` failing inside the VM" confusion.
6. **Port forwards are automatic for loopback.** Any TCP port the guest binds gets forwarded to the host's `127.0.0.1` automatically. You only need explicit `portForwards:` to remap ports or expose on `0.0.0.0`.
7. **Networking choice depends on who needs to reach whom.** Default user-mode is fine for "guest reaches internet, host reaches guest on localhost." For LAN visibility or VM↔VM, you need `socket_vmnet`.

---

## Networking Decision Shortcuts

Pick a mode by what you need to reach:

- "Linux dev box, no LAN exposure" → user-mode (default). Don't add `networks:`.
- "iPhone on same Wi-Fi reaches a server in the VM" → `socket_vmnet bridged`.
- "Two Lima VMs talk to each other but stay off LAN" → `socket_vmnet shared` or `host`.
- "Maximum performance, no LAN exposure" → `vzNAT: true` (vz only).

For the full mode table, decision rationale, `host.lima.internal` semantics, and the auto-port-forward deny-list, see `references/networking.md`.

---

## Where to dive deeper

Each reference file below is loaded on demand. Read the one that matches the current task — they don't duplicate content from this file or each other; they cross-link where needed.

- **`references/installation.md`** — `brew install` steps, optional `lima-additional-guestagents` for cross-arch guests, and `socket_vmnet` sudoers setup.
- **`references/lifecycle.md`** — the `limactl` command surface: `start`, `stop`, `list`, `shell`, `edit` (including `--set` patches), `delete`, `validate`, `factory-reset`, plus where on disk Lima stores per-VM state.
- **`references/lima-yaml.md`** — annotated `lima.yaml` fields, the `provision.mode` table, the robust group-add pattern for adding the in-guest user to a group like `docker`, and the `~/.lima/_config/override.yaml` workflow for opting out of the `lima` username remap.
- **`references/networking.md`** — full networking modes table, `host.lima.internal` resolver behavior, and auto-port-forward semantics + deny-list.
- **`references/mounts.md`** — virtiofs vs 9p vs reverse-sshfs, APFS case-insensitivity pitfalls, and `mountInotify`.
- **`references/workflows.md`** — common workflows: default Ubuntu VM, Docker host VM, running background processes from a single shell call, editing an existing VM's resources, x86_64 binaries via Rosetta, validating YAMLs.
- **`references/troubleshooting.md`** — log file locations, the read-stdout-first rule for startup failures, symptom→fix table, common gotchas, and the pre-mutation safety checklist.

VM data lives at `~/.lima/<name>/` — `lima.yaml` (resolved config), `diffdisk` (qcow2 disk), `serial.log` (boot console), `ha.stderr.log` / `ha.stdout.log` (host agent logs). When troubleshooting, those logs are where the answers live (see `references/troubleshooting.md`).
