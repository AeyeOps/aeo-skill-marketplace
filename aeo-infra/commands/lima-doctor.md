---
name: lima-doctor
version: 0.2.0
description: Run a pre-flight + state check for Lima on this Apple Silicon Mac and recommend next actions based on what's found.
---

The user invoked `/lima-doctor`. They want a concrete diagnostic of where their Lima setup stands. Ground yourself in the `aeo-infra:lima-vm-operations` skill — its Pre-Flight section is the source of truth for what to check — then run those checks plus `limactl list 2>/dev/null` and `brew list --versions socket_vmnet lima-additional-guestagents 2>/dev/null` (in parallel where possible) and report:

- **Host fitness** — arm64 + macOS 13+ → PASS/FAIL with the reason
- **Install state** — Lima version (or "not installed"); note `socket_vmnet` and `lima-additional-guestagents` separately
- **Username remap** — does `id -un` match `^[a-z_][a-z0-9_-]*$`? If not, the in-guest user will be remapped to `lima` — say so explicitly
- **VMs present** — table of name/status/cpus/memory, or "none"
- **Recommended next actions** — max 3, tailored to what was found (e.g. "Lima not installed → `brew install lima`"; "VM `mydev` is Stopped → `limactl start mydev`"; "Username will remap → write provisioning scripts targeting `lima`, not your macOS username")

Under 250 words. Read-only command: propose mutations, do not perform them.
