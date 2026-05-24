# Joining a headscale-controlled mesh from macOS

Covers the actual `tailscale up` call against a self-hosted headscale
coordinator, the deep-link fallback when the CLI cannot drive the daemon, the
preauth-key gotcha on recent headscale builds, and verification commands.

Assumes the install is already clean per
[installing-tailscale-on-macos.md](installing-tailscale-on-macos.md) — i.e.
the four verification checks at the bottom of that file all pass.

---

## CLI binary on macOS

The same binary `/Applications/Tailscale.app/Contents/MacOS/Tailscale` acts
as both the GUI app (when launched via `open -a`) and the CLI (when invoked
with arguments). The operator-friendly path is the symlink
`/usr/local/bin/tailscale`, which the GUI installs on demand:

> Tailscale.app menu bar → Preferences → General → **Install command line tool**

Until that has been clicked once, refer to the binary by full path. Calls
that mutate state (`up`, `down`, `set`) require root:

```sh
sudo /Applications/Tailscale.app/Contents/MacOS/Tailscale up [flags]
```

Read-only calls (`status`, `ip`, `ping`) work without root.

---

## Preauth key minting on headscale

On the headscale host, mint a single-use 1-hour key:

```sh
headscale preauthkeys create --user <numeric-user-id> --expiration 1h
```

### Gotcha: `--user` is numeric on recent headscale builds

Older headscale CLI accepted `--user <name>`; current builds parse `--user`
as an unsigned integer (the user's row ID) and reject names with
`invalid argument "<name>" for "-u, --user" flag: strconv.ParseUint`. List
users first to find the right ID:

```sh
headscale users list
# example output:
# ID | Name | Username | Email | Created
# 1  |      | mesh     |       | 2026-01-21 06:24:45
```

The ID is the leftmost column, not the Name or Username. Pass that integer
to `preauthkeys create`. Other useful flags: `--reusable` (omit for
single-use), `--expiration 24h` (longer than the default 1h), `--ephemeral`
(node auto-removed when offline).

---

## Joining: preauth-key CLI path (primary)

With a fresh key and a healthy daemon:

```sh
sudo /Applications/Tailscale.app/Contents/MacOS/Tailscale up \
  --login-server=https://<headscale-host> \
  --auth-key=<preauth-key> \
  --accept-routes \
  --ssh \
  --hostname=<this-host>
```

Flag notes:

- `--login-server` is what tells the daemon to use headscale instead of the
  public Tailscale control plane. The host must serve valid TLS reachable
  from this machine.
- `--auth-key` consumes the preauth key. If it is rejected as expired or
  consumed, mint a new one — single-use keys are spent on the first
  successful contact even if the local invocation appears to hang.
- `--ssh` enables Tailscale SSH server on this host, making it reachable
  from other mesh peers via `tailscale ssh` or any wrapper that uses
  Tailscale identity (e.g., the AeyeOps `tssh` script if present in the
  environment). Without this flag the host can connect outbound but cannot
  accept inbound Tailscale SSH.
- `--accept-routes` causes this host to install routes advertised by other
  peers (subnet routers). Safe to include on a leaf client.
- `--hostname` overrides the OS hostname for mesh identity. Without it the
  registration uses whatever `hostname` returns.

A successful run returns immediately (no output beyond a possible auth-URL
fallback). Verify with `tailscale status`.

---

## Joining: deep-link fallback (when CLI cannot drive the daemon)

If the daemon is up but the CLI keeps returning "failed to connect to local
tailscale service" — typically because an OS permission grant is still
pending and the CLI's local IPC handshake is being blocked — there is a
GUI-driven workaround that uses the app's URL handler.

```sh
open "tailscale://changelogin?server=https://<headscale-host>"
```

This deep link instructs Tailscale.app to switch its coordination server to
headscale and surface a "Sign in" prompt in the menu bar. From there:

1. Click the Tailscale menu-bar icon → **Sign in**.
2. The system browser opens a URL of the form
   `https://<headscale-host>/register/nodekey:<long-hex>`.
3. The headscale page displays the nodekey and instructions for
   registration.
4. On the headscale host, register the nodekey to the desired user:
   ```sh
   headscale nodes register --user <numeric-user-id> --key nodekey:<long-hex>
   ```
5. The browser page refreshes to "success", and the menu-bar Tailscale icon
   transitions to the connected state.

This path works around any CLI-to-daemon IPC issue because the GUI app
itself initiates the registration via the deep link.

---

## Verification

After joining, confirm all of the following:

```sh
# 1. Status shows this host plus expected peers
/Applications/Tailscale.app/Contents/MacOS/Tailscale status

# 2. This host has a tailnet IP
/Applications/Tailscale.app/Contents/MacOS/Tailscale ip -4

# 3. Outbound to a known-good peer
/Applications/Tailscale.app/Contents/MacOS/Tailscale ping -c 2 <peer-hostname>

# 4. Tailnet egress is on the Tailscale utun interface, not the physical NIC
route -n get 100.64.0.1 | grep interface
#    expect: interface: utunN

# 5. Inbound reach (from any other mesh peer running tailscale ssh)
#    On the peer:  tailscale ssh <this-hostname> hostname
#    expect:       <this-hostname>
```

If verification (5) fails but (3) succeeds, the `--ssh` flag was likely
omitted on the `up` call. Re-run `tailscale up` adding `--ssh`, or use
`tailscale set --ssh=true` to flip just that flag without a full re-join.

---

## Logout / re-join

To switch coordination servers, change hostnames, or burn down state and
start over:

```sh
sudo /Applications/Tailscale.app/Contents/MacOS/Tailscale logout
```

This returns the daemon to a logged-out state without uninstalling
anything. A subsequent `tailscale up` with new flags re-registers.

To also delete the node entry on headscale (so the same hostname can
re-register cleanly):

```sh
# On the headscale host:
headscale nodes list                              # find the node ID
headscale nodes delete --identifier <node-id>
```
