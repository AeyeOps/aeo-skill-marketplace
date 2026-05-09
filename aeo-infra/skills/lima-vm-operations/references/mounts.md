# Mounts

Loaded from `SKILL.md`. Mount types, the `writable: false` footgun, APFS case-sensitivity gotchas, and `mountInotify`. For the `mounts:` field shape and how it sits inside `lima.yaml`, see `lima-yaml.md`.

Lima maps host paths into the guest. Mounts are an explicit list — there is no implicit `~` passthrough beyond the default Lima adds for you.

```yaml
mounts:
  - location: "~"               # mounts host $HOME at the same path inside guest
    writable: false             # default; explicit for clarity
  - location: "/tmp/lima"
    writable: true
  - location: "~/Developer"
    writable: true
    mountPoint: "/srv/code"     # remap to a different path inside guest
```

| Mount type | When used | Speed | Notes |
|------------|-----------|-------|-------|
| `virtiofs` | vz, macOS 13+ | Fastest | Best POSIX semantics; the right default on Apple Silicon |
| `9p` | qemu | Medium | Used when vz isn't available |
| `reverse-sshfs` | Legacy fallback | Slowest | Lima's pre-virtiofs default; rarely the right choice now |

Set globally via top-level `mountType: virtiofs` (or per-VM via `limactl edit` — see `lifecycle.md`). **`mountType` is a top-level field, NOT a per-mount-entry field** — putting it inside a `mounts:` list item makes the validator reject the YAML with `unknown field "mountType"`. With `vmType: vz`, Lima already picks `virtiofs` — only override if you have a specific reason.

## Pitfalls

- **APFS case-insensitivity travels through virtiofs.** macOS APFS is case-insensitive by default. A guest tool that depends on case-sensitive filenames (some Java builds, some npm packages) can break on a virtiofs mount of an APFS path. Workaround: use a separate APFS volume formatted case-sensitive, or do the work inside the VM's own disk (under the in-guest user's home — `/home/<user>/` for unmapped names, `/home/lima/` when Lima remapped your macOS username; see SKILL.md's "Username gotcha") and only sync results back.
- **`writable: false` is the silent footgun.** A mount marked read-only fails writes silently — file operations return `EROFS`, and tools' error messages are often unhelpful. Always confirm `writable: true` is set when the guest needs to write.
- **`mountInotify: true` (top-level)** enables file-change notifications across the boundary. Off by default — turn it on for dev loops that rely on file watchers.
