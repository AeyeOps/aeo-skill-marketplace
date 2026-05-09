# Configuring a VM (`lima.yaml`)

Loaded from `SKILL.md`. Annotated config example, key field reference, the `provision.mode` table, the group-add provisioning pattern, and the `~/.lima/_config/override.yaml` workflow for opting out of the `lima` username remap.

A minimal Apple-Silicon-friendly config (the values below are *example* tunings, not Lima's defaults — Lima's built-in defaults are 4 CPUs / 4 GiB RAM / 100 GiB disk):

```yaml
# ~/dev/my-dev.yaml
vmType: vz
cpus: 4
memory: 8GiB                  # tuned up from default 4GiB for build workloads
disk: 60GiB                   # tuned down from default 100GiB; sparse anyway

# Lima auto-selects the arm64 image from this list on Apple Silicon
images:
  - location: "https://cloud-images.ubuntu.com/releases/24.04/release/ubuntu-24.04-server-cloudimg-arm64.img"
    arch: "aarch64"
  - location: "https://cloud-images.ubuntu.com/releases/24.04/release/ubuntu-24.04-server-cloudimg-amd64.img"
    arch: "x86_64"

mounts:
  - location: "~"
    writable: false             # default — host's home read-only inside guest
  - location: "~/Developer"
    writable: true              # writable mount for active project work
    mountPoint: "/mnt/Developer"

# Default networking is user-mode (vzNAT under vz). No `networks:` block needed
# unless you want shared/bridged/host. host.lima.internal works regardless.

# Optional: explicit port forward (most ports auto-forward to 127.0.0.1 on host)
portForwards:
  - guestPort: 8080
    hostIP: "0.0.0.0"           # bind on all host interfaces, not just loopback
    hostPort: 18080

# Optional: cloud-init style provisioning that runs on first boot
provision:
  - mode: system          # see provision.mode table below
    script: |
      #!/bin/bash
      set -eux
      apt-get update
      apt-get install -y build-essential git

# Optional: enable Rosetta so x86_64 Linux binaries run on Apple Silicon
rosetta:
  enabled: true
  binfmt: true
```

## Key Fields, Annotated

| Field | Purpose | Apple-Silicon default |
|-------|---------|-----------------------|
| `vmType` | Hypervisor backend | `vz` (set explicitly to be safe) |
| `cpus` | vCPUs | `4` |
| `memory` | RAM, e.g. `4GiB` | `4GiB` (bump to 8+ for build workloads) |
| `disk` | Virtual disk size | `100GiB` (sparse, only consumes what's used) |
| `images` | List of cloud image URLs; Lima picks by arch | Always include both `aarch64` and `x86_64` for portability |
| `mounts` | Host paths exposed to guest | `~` mounted read-only; opt in to `writable: true` per path |
| `mountType` | Filesystem protocol | `virtiofs` (vz) / `9p` (qemu) — usually leave to default |
| `networks` | Extra NICs | Empty (user-mode NAT). Add `vzNAT: true` or `lima: shared/bridged/host` as needed |
| `portForwards` | Explicit forwards | Empty (loopback auto-forward covers most cases) |
| `provision` | First-boot scripts | Empty |
| `containerd` | Built-in nerdctl | `{ system: false, user: true }` (matches templates) |
| `rosetta` | x86_64 emulation | Disabled — enable for x86 Docker images, etc. |

`limactl edit <name>` accepts most of these post-creation; the immutable ones are listed in `lifecycle.md`. For the mount type details (virtiofs vs 9p vs reverse-sshfs) see `mounts.md`.

## `provision.mode` values

| Mode | Runs as | When | Typical use |
|------|---------|------|-------------|
| `system` | root | First boot, after cloud-init | Install packages, write `/etc/...` |
| `user` | the in-guest user | First boot, after `system` scripts | Per-user dotfiles, `~/.config` setup |
| `boot` | root | **Every** boot, before user login | Re-apply firewall rules, mount network shares |
| `dependency` | root | Before other modes; ordered first | Ensure a tool is present before later scripts use it |
| `data` | n/a (writes a file, not a script) | First boot | Write fixed content to a guest path (e.g. config file) |
| `ansible` | n/a (runs an Ansible playbook) | First boot | Apply an existing playbook against the guest |

`system` is the right default for "install Docker"–style work. Use `user` only when the action genuinely requires the in-guest user's identity (e.g. setting up `~/.ssh/`).

## Adding the in-guest user to a group (e.g. `docker`)

A common provision step is "install Docker, add the user to the `docker` group." Two non-obvious traps make this harder than it looks on Lima:

1. The validator will reject scripts that reference `LIMA_CIDATA_USER` or other `LIMA_CIDATA_*` variables — Lima treats those as private internals. So you can't just `usermod -aG docker $LIMA_CIDATA_USER`.
2. UID-based filters are tempting but fragile. macOS hosts mirror the host UID (typically 501–502) into the guest, so `$3 >= 1000` silently misses the in-guest user. Widening to `$3 >= 500` then catches Ubuntu/Debian system daemons (`systemd-network` 998, `systemd-timesync` 996, etc.) which sit in the same band and appear *first* in `/etc/passwd` — `awk ... { exit }` matches them and adds *systemd-network* to docker, not your user. Both fail silently under `set -eux`.

The robust pattern is to identify the in-guest user by **home directory under `/home/` plus an interactive login shell** — system daemons have `nologin` shells and live outside `/home`, so this filter selects unambiguously regardless of UID layout:

```yaml
provision:
  - mode: system
    script: |
      #!/bin/bash
      set -eux
      if ! command -v docker >/dev/null 2>&1; then
        curl -fsSL https://get.docker.com | sh
      fi
      # Pick the in-guest user by home-in-/home + interactive shell.
      # UID-based filters are unreliable: macOS-mirrored UIDs (501-ish) collide
      # with Ubuntu/Debian's 100-999 system-user band.
      LIMA_USER=$(awk -F: '$6 ~ /^\/home\// && $7 ~ /(bash|sh|zsh|dash)$/ { print $1; exit }' /etc/passwd)
      if [ -z "$LIMA_USER" ]; then
        echo "ERROR: could not identify in-guest user" >&2
        exit 1
      fi
      usermod -aG docker "$LIMA_USER"
```

The explicit `exit 1` on no-match turns a silent failure into a hard one, which `set -e` will catch. **Always test the resulting `groups` output before trusting that group membership took.**

**Verification quirk** worth knowing: right after the provision script runs, `limactl shell <name> -- groups` may show *stale* group membership that excludes the new group. This is because `limactl` opens a multiplexed SSH ControlMaster session early in boot — before `usermod` ran — and supplementary groups are evaluated when that session is created. To verify correctly:

- `limactl shell <name> -- sudo -u <user> -i groups` (forces a fresh login shell), or
- `limactl stop <name> && limactl start <name>` then re-check.

Don't conclude the provision failed just because the first `limactl shell ... groups` doesn't show the new group.

This pattern works whether your macOS username produces a real Linux username or got remapped to `lima` (see SKILL.md's "Username gotcha" or the override.yaml section below).

## Opting out of the `lima` username remap (`override.yaml`)

To give the in-guest user a custom name instead of the silent `lima` fallback, write `~/.lima/_config/override.yaml`. Lima overlays it onto every newly-created VM; existing VMs keep their resolved user, and reverting is a `rm` away.

When a user wants this set up, gather the inputs from their host directly rather than asking them to look it up — `id -un`, `id -u`, and `id -F 2>/dev/null` give you the macOS username, UID, and full name. Derive a Linux-valid name by lowercasing `id -un` and dropping invalid characters (e.g. `Jane.Doe` → `jane`, or `j.smith` → `jsmith`/`smith`), confirm the choice with the user, then write:

```yaml
# ~/.lima/_config/override.yaml
user:
  name: <derived-name>      # must match ^[a-z_][a-z0-9_-]*$
  uid: <id-u-output>        # match host UID for virtiofs ownership
  comment: "<id-F-output>"
```

The robust group-add pattern earlier in this file works regardless of in-guest username, so this override is purely about ergonomics (shell prompt, SSH config, `~` mount path), not correctness.
