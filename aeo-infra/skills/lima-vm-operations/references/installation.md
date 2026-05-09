# Installation

Loaded from `SKILL.md`. Covers `brew install lima`, optional `lima-additional-guestagents` for cross-arch guests, and the `socket_vmnet` sudoers setup required for shared/bridged/host networking.

```bash
# 1. Install Lima itself
brew install lima

# 2. Verify
limactl --version                                  # expect 2.1.x or newer
limactl info | jq '{version,driver:.driver}'       # version + active driver (vz/qemu)
# `limactl info` without jq prints a large JSON blob (template metadata) — pipe to jq.

# Optional but recommended on Apple Silicon: extra guest agents for non-native arches.
# Required for running x86_64 Linux guests, and for some Rosetta workflows.
brew install lima-additional-guestagents

# 3. (Optional) Install socket_vmnet — only needed for shared/bridged/host networks
brew install socket_vmnet
# socket_vmnet runs as a privileged daemon. Configure sudoers per its post-install message
# (typically: limactl sudoers | sudo tee /etc/sudoers.d/lima)
limactl sudoers --check                            # verify sudoers is set up correctly
```

`brew install lima` pulls in `qemu` as a dependency for the `qemu` driver and as a fallback. The `vz` driver uses Apple's framework directly — no qemu involved on the runtime path.

`socket_vmnet` is **not** required for the default user-mode network. Skip step 3 unless you specifically need shared/bridged/host networking — see `networking.md` for which modes require it.

**Sudoers setup pitfall:** the `limactl sudoers` line is *not* run automatically by `brew install socket_vmnet` — its post-install message is easy to miss. If `socket_vmnet`-backed networks fail at start with `failed to start the daemon`, this is almost always the cause; run `limactl sudoers --check` to confirm.
