# VM Lifecycle Commands

Loaded from `SKILL.md`. The `limactl` command surface for creating, listing, shelling into, editing, and deleting VMs, plus the on-disk layout of per-VM state.

```bash
# Create + start the default Ubuntu VM (interactive prompts on first run)
limactl start                                   # launches default template

# Start a named VM from a built-in template, non-interactively.
# Note: Lima 2.0+ uses `template:<name>` syntax. The older `template://<name>`
# form still works but emits a deprecation warning — always use `template:`.
limactl start --name=docker template:docker --tty=false

# Start from a local YAML
limactl start --name=mydev ./my-dev.yaml --tty=false

# List VMs and their state
limactl list                                    # ls is an alias

# Shell into a VM (long form)
limactl shell mydev

# Run a single command in a VM
limactl shell mydev -- uname -a

# Short-form: `lima` is shorthand for `limactl shell <default-vm>`
lima uname -a                                   # runs in the "default" VM

# Stop a VM (state preserved)
limactl stop mydev

# Delete a VM (irreversible — disk image and config gone)
limactl delete mydev                            # add --force to skip confirmation

# Edit a stopped VM's YAML in $EDITOR
limactl edit mydev

# Patch a single field non-interactively (yq-style expression)
limactl edit mydev --set '.cpus = 8 | .memory = "16GiB"'

# Validate a YAML before using it
limactl validate ./my-dev.yaml

# Reset everything — wipe all VMs (use with care; see troubleshooting.md)
limactl factory-reset
```

## Per-VM state on disk

VM data lives at `~/.lima/<name>/`:

| File | Purpose |
|------|---------|
| `lima.yaml` | Resolved config (after templates and overrides applied) |
| `diffdisk` | The qcow2 disk image |
| `serial.log` | Boot console output (kernel panics, cloud-init errors) |
| `ha.stderr.log` / `ha.stdout.log` | Host agent logs — post-launch failures land here |
| `cidata.iso` | Generated cloud-init seed |
| `_disks/` | Additional persistent disks attached to the VM |

When troubleshooting startup failures, these logs are where the answers live — see `troubleshooting.md` for the read order.

## Editing an already-created VM

`limactl edit <name>` accepts most fields post-creation, but a few — `vmType`, `disk` size *shrinks*, and the `images:` list once a disk has been provisioned — are immutable. To change those, `limactl delete` and recreate (the data on the disk is gone either way). See `lima-yaml.md` for which fields tolerate edits.
