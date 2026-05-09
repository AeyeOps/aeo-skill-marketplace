# Common Workflows

Loaded from `SKILL.md`. The recipes below combine the lifecycle commands (`lifecycle.md`), config fields (`lima-yaml.md`), and networking choices (`networking.md`) into common end-to-end flows.

## Spin up the default Ubuntu VM (fastest possible start)

```bash
limactl start --tty=false
limactl shell default
```

The `default` template lands you in the current Ubuntu cloud image (LTS or interim release depending on Lima version), with `~` mounted (read-only), nerdctl-rootless preinstalled, and user-mode networking.

> **Important — LTS:** `template:default` is **not pinned to LTS**. If your work assumes Ubuntu LTS package availability, EOL timeline, or kernel version, base your YAML on an explicit LTS image URL (e.g. `ubuntu-24.04-server-cloudimg-arm64.img`) — do not rely on `template:default`.

## Start a Docker-host VM and use it from the host

```bash
limactl start --name=docker template:docker --tty=false
# Lima prints the DOCKER_HOST instructions; usually:
export DOCKER_HOST=$(limactl list docker --format 'unix://{{.Dir}}/sock/docker.sock')
docker run --rm hello-world
```

## Run a background process inside the guest from a single shell call

`limactl shell <name> -- bash -c '<cmd> &'` is a foot-gun: the SSH channel stays open waiting for the backgrounded process, and the command often returns exit `255` after the shell harness gives up. The reliable pattern is `nohup ... & disown`:

```bash
limactl shell mydev -- bash -c 'nohup python3 -m http.server 8080 >/tmp/http.log 2>&1 & disown'
```

`nohup` detaches from the controlling terminal, the `&` backgrounds, and `disown` removes it from the shell's job table so the SSH channel can close cleanly.

## Edit an existing VM to add resources

```bash
limactl stop mydev
limactl edit mydev --set '.cpus = 8 | .memory = "16GiB"'
limactl start mydev
```

Some fields are immutable post-create (`vmType`, base `images:`, `disk` shrinks) — see `lifecycle.md`.

## Run an x86_64 binary on Apple Silicon

```yaml
# In lima.yaml
rosetta:
  enabled: true
  binfmt: true                 # registers Rosetta as x86_64 binfmt handler in guest
```

After `limactl start`, x86_64 binaries (and x86 Docker images via `--platform linux/amd64`) execute via Rosetta translation in the guest.

If you're spinning up a fully x86_64 Linux *guest* (rather than running x86 binaries inside an arm64 guest), you also need the foreign-arch guest agents — install them via `brew install lima-additional-guestagents` (see `installation.md`). Lima's `brew install` post-message mentions this; it's easy to miss but required for cross-arch guests.

`rosetta: { enabled: true, binfmt: false }` installs Rosetta into the guest but doesn't wire it up as the binfmt handler — you'd have to register it manually. Almost always you want both `enabled: true` and `binfmt: true`.

## Validate a YAML before committing

```bash
limactl validate ./my-dev.yaml
```

Catches typos, unknown fields, and references to forbidden internals (e.g. `LIMA_CIDATA_*` env var references in provision scripts emit a clear validator warning). It does **not** verify that the host arch matches an `images:` entry, that URLs reach a real image, or that mount paths exist on the host — those are runtime concerns that `limactl start` will surface in its own stdout. (See Core Principle 3 in `SKILL.md` and `troubleshooting.md` for the read-stdout-first rule.)
