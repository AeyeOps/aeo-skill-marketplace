# Networking Modes

Loaded from `SKILL.md`. Pick a mode by **what you need to reach**, not by what sounds powerful. The decision shortcuts in `SKILL.md` cover the common cases; this file is the full reference.

| Mode | Config | Guest → Internet | Guest → Host | Host → Guest | LAN devices ↔ Guest | VM ↔ VM | Needs `socket_vmnet`? |
|------|--------|------------------|--------------|--------------|---------------------|---------|------------------------|
| **User-mode (default)** | (no `networks:` block) | yes (NAT) | yes via `host.lima.internal` | yes on `127.0.0.1` (auto port-forward) | no | no | no |
| **vzNAT** | `networks: [{ vzNAT: true }]` | yes (NAT, faster) | yes via `host.lima.internal` | yes on `127.0.0.1` | no | no | no (vz only) |
| **socket_vmnet shared** | `networks: [{ lima: shared }]` | yes | yes (`192.168.105.1`) | yes on shared subnet | no | yes | yes |
| **socket_vmnet bridged** | `networks: [{ lima: bridged, interface: en0 }]` | yes | yes | yes | yes — VM gets a real LAN IP via DHCP | yes | yes |
| **socket_vmnet host** | `networks: [{ lima: host }]` | no | yes | yes | no | yes | yes |

For the `socket_vmnet` setup itself (`brew install`, sudoers fragment), see `installation.md`.

## `host.lima.internal`

A stable hostname inside the guest that resolves to the host's address on the user-mode/vzNAT NAT — `192.168.5.2` in current Lima releases. Use it instead of guessing IPs. It works regardless of which network mode you've added, and it resolves through **both** the guest's `/etc/hosts` and Lima's in-VM hostResolver (so `getent hosts host.lima.internal`, `curl http://host.lima.internal/`, and `dig host.lima.internal` all return the same answer). You don't need to debug DNS configuration to use it.

If `host.lima.internal` doesn't resolve, the cause is almost always a top-level `hostResolver: { enabled: false }` override — the default is enabled, so leaving the field unset is the right move.

## Auto port-forward

Lima watches `ss -tnlp` inside the guest and forwards any new TCP listener to the host's `127.0.0.1:<same port>` via SSH. This includes listeners bound only to the guest's `127.0.0.1` — those are forwarded the same as `0.0.0.0` listeners. The forward typically appears within 1–3 seconds of the guest listener; if it's still missing after ~10 seconds, grep `Not forwarding` in `~/.lima/<name>/ha.stderr.log` to see why Lima skipped it.

### Auto-forward deny-list

Two well-known guest listeners are *intentionally* excluded so they don't collide with services on your Mac:

- `0.0.0.0:22` — guest's sshd (Lima uses its own forwarded SSH port for `limactl shell`).
- `127.0.0.53:53` and `127.0.0.54:53` — systemd-resolved on the guest.

Everything else — including guest-loopback-only listeners — auto-forwards. To remap a port, or to bind on `0.0.0.0` on the host instead of loopback, add an explicit `portForwards` entry. The `hostIP` field defaults to `127.0.0.1` if omitted; set `0.0.0.0` to expose on all host interfaces.

## Multi-VM caveat

Don't run more than one Lima VM with `vzNAT` on the same host — vzNAT picks a fixed subnet (192.168.105.x) and overlap causes routing weirdness. Use `socket_vmnet shared` for multi-VM scenarios where the VMs need to talk to each other.
