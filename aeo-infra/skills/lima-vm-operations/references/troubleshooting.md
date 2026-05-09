# Troubleshooting

Loaded from `SKILL.md`. Where to read first when `limactl start` fails or a VM never reaches `Running`, plus the symptom→fix table, the common-gotchas list, and the pre-mutation safety checklist.

## Read order for startup failures

```bash
# 0. READ THE limactl start STDOUT FIRST. Pre-launch failures (image-arch mismatch,
#    bad image URL, schema rejection) print on the start command itself and never
#    reach the log files — those files only get created once the VM begins booting.

# 1. Host agent logs (post-launch failures land here)
tail -100 ~/.lima/<name>/ha.stderr.log

# 2. Boot console (kernel panics, cloud-init errors)
tail -200 ~/.lima/<name>/serial.log

# 3. Re-run with debug logging
limactl --debug start <name>

# 4. If the VM was half-created and is wedged, stop and delete
limactl stop --force <name>
limactl delete --force <name>
```

The order matters: reaching for `ha.stderr.log` before reading the `limactl start` output often finds the file doesn't exist yet (the VM never made it that far), and concludes the tooling is broken when the actual error was already on screen. (See `lifecycle.md` for what each log file holds.)

## Symptom → fix

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `vmType "vz" requires macOS 13.0` | Old macOS | Upgrade macOS, or set `vmType: qemu` |
| `failed to start the daemon` (socket_vmnet) | sudoers not configured | `limactl sudoers \| sudo tee /etc/sudoers.d/lima`, then `limactl sudoers --check` (see `installation.md`) |
| Boot hangs at "cloud-init" | Provision script hung | Check `serial.log` for the script's stderr; fix and `limactl factory-reset && limactl start ...` |
| Image download fails / 404 | Image URL moved | Update `images:` URLs to current cloud-image release path |
| `unsupported arch: "x86_64"` (or similar arch-mismatch) | No `aarch64` entry in `images:` | Add an `arch: "aarch64"` image to `images:` |
| Mount writes fail with `EROFS` | `writable: true` missing | Add `writable: true` to the mount entry, then `limactl restart <name>` (see `mounts.md`) |
| `host.lima.internal` doesn't resolve in guest | DNS resolver disabled | Confirm top-level `hostResolver: { enabled: true }` or stick to default (it's enabled by default; see `networking.md`) |
| Auto port-forward doesn't expose LAN access | Forwards bind to `127.0.0.1` only | Add explicit `portForwards: [{ guestPort: N, hostIP: "0.0.0.0", hostPort: N }]` |
| `limactl edit` errors "VM is running" | Some fields require stopped VM | `limactl stop <name>`, edit, `limactl start <name>` |
| Performance feels slow on large file ops | Using qemu + 9p instead of vz + virtiofs | Set `vmType: vz`; recreate VM (vmType is immutable post-creation) |
| `limactl start` exits fatal with "boot scripts must have finished" / cloud-init timeout | Heavy `provision:` script (e.g. `get.docker.com` + containerd) exceeds Lima's foreground boot-scripts timeout (~10 min) | Don't recreate. Run `limactl shell <name> -- cloud-init status --wait` to see if cloud-init is still running; once `done`, the VM is usable. To avoid the foreground timeout next time, use `mode: boot` or `mode: dependency` for fast-path setup and let heavier installs run after the boot gate (see `lima-yaml.md` for `provision.mode`). |

## Common Gotchas

- **`vmType` is immutable post-create.** If you started with the default and want to switch vz↔qemu, you must `limactl delete` and recreate. Plan ahead.
- **`limactl start` with no args starts `default`**, creating it from `template:default` if it doesn't exist. To start a *different* template, you must pass `template:<name>` or a YAML path.
- **`lima` (the short command) only targets the `default` VM.** For named VMs, use `limactl shell <name>` or set `LIMA_INSTANCE=<name>`.
- **Templates are bundled locators of the form `template:<name>`**, not file paths. They resolve to YAMLs shipped inside the Lima install. List with `limactl create --list-templates`. Pre-2.0 Lima used `template://<name>` (with the slashes); 2.0+ accepts both but warns on the old form — always use `template:<name>` in new code.
- **`socket_vmnet` requires sudo.** Without a configured sudoers fragment, shared/bridged/host networks fail at start. The setup is one command (`limactl sudoers | sudo tee ...`) but is not done by `brew install` (see `installation.md`).
- **`writable: false` is the silent footgun.** Default mount mode is read-only. Plenty of "why doesn't this work" hours have been lost here (see `mounts.md`).
- **Rosetta requires `binfmt: true`** to actually intercept x86 binaries in the guest. `enabled: true` alone installs Rosetta but doesn't wire it up.
- **APFS case-insensitivity travels through virtiofs.** If a guest build expects case-sensitive paths and the source lives on case-insensitive APFS, the VM inherits that (see `mounts.md`).
- **Don't run more than one Lima VM with `vzNAT` on the same host** — vzNAT picks a fixed subnet (192.168.105.x) and overlap causes routing weirdness. Use `socket_vmnet shared` for multi-VM scenarios (see `networking.md`).
- **`limactl factory-reset` deletes every VM.** It is not a "reset this VM" command. To reset one VM, `limactl delete <name> && limactl start <name>`.

## Pre-Mutation Safety Checklist

Before any command that destroys VM state:

```bash
# 1. Confirm which VM you're about to touch
limactl list

# 2. For delete: check it's the right one
limactl shell <name> -- hostname  # last sanity check

# 3. Stop before delete (limactl delete on a running VM forces a kill)
limactl stop <name>
limactl delete <name>

# 4. Never run factory-reset without explicit confirmation — it's all-VMs
```

`limactl delete` is irreversible — the disk image is gone. If the VM has uncommitted work, copy it out via `limactl shell <name> -- tar -czf - /path | tar -xzf - -C ~/backup` first.
