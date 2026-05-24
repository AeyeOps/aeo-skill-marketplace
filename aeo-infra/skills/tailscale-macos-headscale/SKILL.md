---
name: tailscale-macos-headscale
description: |
  Onboard a macOS host (Tahoe / macOS 26 and later) as a Tailscale client of a
  self-hosted headscale control plane. Covers Tailscale.app installation via
  Homebrew Cask, the NetworkExtension permission grants required for the daemon
  to start, the conflict that arises if the brew formula `tailscale` is also
  installed alongside the cask, how to use `tailscale up --login-server` with
  a headscale preauth key, the deep-link fallback flow when the CLI cannot
  reach the daemon, the headscale-specific gotcha that `headscale preauthkeys
  create --user <N>` expects a numeric user ID rather than a username on
  recent builds, and bidirectional reach verification once joined.
  Use when adding a macOS host to a headscale-controlled mesh, troubleshooting
  symptoms like "failed to connect to local tailscale service", Tailscale.app
  stuck on "Starting...", `tailscale up` hanging on "joining <coordinator>", a
  blank menu-bar icon after a fresh install, deciding between the Homebrew
  cask and formula distributions, or recovering from a state where both have
  been installed and are fighting for the local IPC socket. Not for: official
  Tailscale (controlplane.tailscale.com) onboarding, which is well documented
  upstream; Tailscale on Linux or Windows; or headscale server-side install.
---

# Tailscale on macOS against a self-hosted headscale

A practical reference for getting a macOS host onto a headscale-managed
Tailscale mesh, with the macOS-specific traps that aren't called out in either
the Tailscale docs (which assume the public control server) or the headscale
docs (which assume Linux clients).

---

## Quick reference

| Item | Value |
|------|-------|
| Recommended client distribution | Homebrew Cask: `brew install --cask tailscale` |
| Do NOT also install | Homebrew formula `tailscale` (its bundled daemon fights the cask's NetworkExtension) |
| App location | `/Applications/Tailscale.app` |
| Bundled CLI binary | `/Applications/Tailscale.app/Contents/MacOS/Tailscale` |
| Operator-friendly CLI shim | `/usr/local/bin/tailscale` — installed via Tailscale menu bar → Preferences → "Install command line tool" |
| Daemon process name (in `ps`) | `IPNExtension` (inside the app bundle) |
| Daemon socket | macOS-internal IPC managed by the NetworkExtension subsystem; not a Unix socket the operator interacts with directly |
| Headscale preauth key minting | `headscale preauthkeys create --user <numeric-id> --expiration 1h` |
| Required permissions before daemon starts | Network Extension allow, VPN configuration approve, system extension activation |

---

## Reference files

| File | Read when |
|------|-----------|
| [installing-tailscale-on-macos.md](installing-tailscale-on-macos.md) | Installing Tailscale fresh, cleaning up a mixed cask+formula install, walking the operator through the macOS permission grants required for the NetworkExtension daemon to start. |
| [joining-headscale-from-macos.md](joining-headscale-from-macos.md) | Connecting a working Tailscale.app to a headscale coordinator — preauth-key CLI flow, deep-link fallback when the CLI cannot reach the daemon, headscale's `--user <id>` vs `--user <name>` pitfall, and verification commands. |

---

## Common tasks

### Install Tailscale for the first time on macOS

1. `brew install --cask tailscale` (the cask, not the formula — see [installing-tailscale-on-macos.md](installing-tailscale-on-macos.md) for why).
2. Open Tailscale.app once: `open -a Tailscale`.
3. Step through the macOS permission grants (Network Extension activation, VPN configuration approval). Detailed paths in [installing-tailscale-on-macos.md](installing-tailscale-on-macos.md).
4. Confirm the daemon is up: `pgrep -fl IPNExtension`.

### Join a headscale-controlled mesh with a preauth key

1. Mint a single-use preauth key on the headscale host (numeric user ID — see [joining-headscale-from-macos.md](joining-headscale-from-macos.md) for the user-id gotcha).
2. `sudo /Applications/Tailscale.app/Contents/MacOS/Tailscale up --login-server=https://<headscale-host> --auth-key=<key> --accept-routes --ssh --hostname=<this-host>`.
3. Verify: `tailscale status` shows the host plus peers.

### Recover from "failed to connect to local tailscale service"

This means the CLI is fine but the NetworkExtension daemon either has not
been activated or has not been granted permission. Procedure in
[installing-tailscale-on-macos.md](installing-tailscale-on-macos.md) under
"Permission dance".

### Recover from a mixed cask + formula install

The brew formula `tailscale` ships its own `tailscaled` that competes with
the cask's NetworkExtension for the local IPC socket. Symptom: Tailscale.app
GUI stuck on "Starting..." and `tailscale up` hangs indefinitely. Full
cleanup steps in [installing-tailscale-on-macos.md](installing-tailscale-on-macos.md).

### Persist Tailscale across reboots

The cask installs a LaunchAgent that auto-starts Tailscale.app on login.
Nothing extra to configure. If using the formula (not recommended), see the
formula's own caveats — not covered here.

---

## Related skills in this marketplace

Cross-skill references in this marketplace use the form
`<skill-name>@<plugin-name>` (e.g., `glinet-slate7@aeo-infra` means the
`glinet-slate7` skill living in the `aeo-infra` plugin).

- `glinet-slate7@aeo-infra` — if Tailscale is being layered on top of a
  WireGuard underlay terminated by a GL-iNet Slate 7 (or other sdk4
  firmware) router, that skill covers the underlay side: client `wg0.conf`
  patterns, the wg-server admin API, peer rotation, and the leak-fix rules
  for Linux clients running Tailscale on top of WireGuard. On macOS the
  leak-fix rules do not apply (macOS routing model differs from Linux
  `ip rule` policy routing), but the WG client config and server
  provisioning are the same.
- `lima-vm-operations@aeo-infra` — if the macOS host is acting as a Lima
  hypervisor and the actual Tailscale client is a Linux VM inside Lima, the
  procedures here do not apply; install Tailscale inside the VM per the
  Linux path instead.
