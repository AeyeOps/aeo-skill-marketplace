---
name: lima
version: 0.2.0
description: Springboard for the lima-vm-operations skill — show what it covers and offer common starting tasks (Apple Silicon Macs).
---

The user invoked `/lima`. They likely want to know what this skill helps with and where to start. Ground yourself in the `aeo-infra:lima-vm-operations` skill before responding, then reply with:

1. One paragraph (1–2 sentences) on what the skill covers and its scope — Apple Silicon Macs, Lima 2.x; Intel/Linux/Colima out of scope.
2. A 4–6 item menu of common starting tasks. Pick from: install + start a default VM, author a custom `lima.yaml` for a Docker host or k8s node, choose a networking mode (user-mode vs `socket_vmnet` shared/bridged), troubleshoot a stuck `limactl start`, add the in-guest user to a group via provision script the right way, switch a VM from `qemu` to `vz`.
3. End by asking the user what they want to do, or — if they're not sure where they stand — suggest running `/lima-doctor` first.

Keep the response under 200 words. This is a menu, not an action: do not run any `brew`, `limactl`, or other shell commands.
