# GL-iNet JSON-RPC API (admin panel backend)

The Slate 7 admin panel is a Vue SPA that drives the device entirely through a JSON-RPC 2.0 API. Anything achievable in the UI is achievable as an HTTP call. Verified on firmware 4.8.x (sdk4); the same API surface is present on most GL-iNet sdk4 devices because they share the `gl-sdk4-ui-*` frontend and the `oui-httpd` backend.

Useful for: scripted provisioning, fleet management, CI checks, headless setup, integrating the router with other automation (Ansible, Home Assistant, n8n).

---

## Endpoint and transport

| Item | Value |
|------|-------|
| URL | `http://<router-ip>/rpc` (default `http://192.168.8.1/rpc`) |
| Method | `POST` |
| Content-Type | `application/json` |
| Protocol | JSON-RPC 2.0 |
| Authentication | Challenge / response → session id (`sid`) |

Authentication is required even from localhost on the device itself.

---

## Request envelope

Two top-level method names matter:

1. **`challenge`** — fetch nonce + salt for login
2. **`login`** — exchange computed hash for an `sid`
3. **`call`** — invoke any module/method with the obtained `sid`

```jsonc
// Generic call
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": ["<sid>", "<module>", "<method>", { /* params object */ }]
}
```

Successful response shape:

```json
{ "id": 1, "jsonrpc": "2.0", "result": { ... } }
```

Error shapes:

```json
{ "id": 1, "jsonrpc": "2.0", "error": { "message": "Access denied", "code": -32000 } }
{ "id": 1, "jsonrpc": "2.0", "error": { "message": "Invalid params", "code": -32602 } }
{ "id": 1, "jsonrpc": "2.0", "result": { "err_msg": "parameter missing", "err_code": 20001011 } }
```

The third shape is the convention for *application-level* errors (returned as `result`, not `error`). Always check both `.error` and `.result.err_code`.

---

## Authentication flow

1. POST `challenge` with `{username}` → receive `{nonce, salt, alg, hash-method}`. `alg=5` corresponds to SHA-256 crypt (Linux `$5$` style).
2. Compute `crypted = crypt(password, "$5$" + salt)` — the full crypt result `$5$<salt>$<hash>`.
3. Compute `hash = sha256(username + ":" + crypted + ":" + nonce)`.
4. POST `login` with `{username, hash}` → receive `{sid, ...}`.
5. Use `sid` as the first array element of every subsequent `call`.

```bash
# Step 1 — challenge
curl -sS -X POST http://192.168.8.1/rpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"challenge","params":{"username":"root"}}'
# → {"result":{"nonce":"...","alg":5,"salt":"...","hash-method":"sha256"}}

# Step 2 — sha256 crypt of password (use openssl, no Python crypt module needed)
crypted=$(openssl passwd -5 -salt "$salt" "$password")

# Step 3 — final hash
hash=$(printf '%s:%s:%s' "root" "$crypted" "$nonce" | sha256sum | awk '{print $1}')

# Step 4 — login
curl -sS -X POST http://192.168.8.1/rpc \
  -H 'Content-Type: application/json' \
  -d "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"login\",\"params\":{\"username\":\"root\",\"hash\":\"$hash\"}}"
# → {"result":{"sid":"...","username":"root","timeout":...,"expire":...}}
```

The `sid` expires after a period of inactivity (usually 5–10 minutes). On expiry, calls return `Access denied` and you should re-issue `challenge` + `login`. A robust client retries once on `Access denied` after re-authenticating.

> Python note: `crypt` was removed in Python 3.13. Use `openssl passwd -5` from shell, or `passlib.hash.sha256_crypt` in Python.

---

## Module discovery

Every loadable RPC module is a file in `/usr/lib/oui-httpd/rpc/` on the router (accessible via SSH). Names without an extension are Lua handlers; `.so` files are compiled C handlers. Both are addressed by their basename in the `call` params.

```bash
ssh root@192.168.8.1 'ls /usr/lib/oui-httpd/rpc/'
# Common modules across sdk4 devices:
#   wg-server.so        wg-client.so         wg_client (lua)
#   ovpn-server.so      ovpn-client.so       ovpn_client (lua)
#   tailscale           zerotier             tor
#   adguardhome         dns                  dhcp
#   firewall            qos                  parental-control
#   modem.so            tethering            multiwan (kmwan)
#   network             wifi                 lan / repeater
#   system              upgrade              cloud
#   plugins.so          luci                 ui
#   black_white_list    clients              edgerouter
```

---

## Method discovery

Two complementary approaches.

### 1. Strings inside the `.so`

```bash
strings /usr/lib/oui-httpd/rpc/wg-server.so |
  grep -E '^(get|set|add|del|list|start|stop|reload|status|generate|create|update|remove|enable|disable|export|configure|init)[a-z_]*$' |
  sort -u
```

That yields the underlying C function names. Most are exposed verbatim as RPC method names.

### 2. Vue bundle reverse-engineering

The frontend ships gzipped Vue bundles in `/www/views/`, one per UI section: `gl-sdk4-ui-<module>.common.js.gz`. They contain every RPC call the UI makes, with parameter shapes inlined.

```bash
# Pull a bundle to a workstation and decompress
ssh root@192.168.8.1 'zcat /www/views/gl-sdk4-ui-wgserver.common.js.gz' > wgserver.js

# Find every call() invocation
grep -oE '"<module>","[a-z_]+"[^)]{0,400}' wgserver.js
# e.g. for wg-server:
#   "wg-server","add_peer",t]
#   "wg-server","generate_peer",t]
#   "wg-server","get_peer_list",{}]

# Find what shape `t` has by walking back to the form definition
python3 -c '
import re
with open("wgserver.js") as f: c = f.read()
i = c.find("submitFormData()")
print(c[i:i+1500])
'
```

This is the fastest way to learn parameter names, validation rules, and which fields are optional.

---

## Common modules and what they do

| Module | Purpose | Notable methods |
|--------|---------|-----------------|
| `wg-server` | WireGuard server (named `wgserver` interface) | `start`, `stop`, `add_peer`, `generate_peer`, `get_peer_list`, `get_status`, `set_setting`, `get_config` |
| `wg-client` | WireGuard client (provider VPN profiles) | `start`, `stop`, `add`, `remove`, `get_status`, `get_list` |
| `ovpn-server` / `ovpn-client` | OpenVPN equivalents | similar shape |
| `tailscale` | Tailscale daemon | `start`, `stop`, `status`, `set_login_server`, `up` |
| `adguardhome` | AdGuard Home | `enable`, `disable`, `get_status` |
| `system` | Reboot, factory reset, hostname, timezone, password | `reboot`, `set_password`, `get_info` |
| `network` | LAN/WAN/zone config | `get_lan`, `set_lan`, `get_wan`, `set_wan` |
| `clients` | Connected client list | `get_list`, `set_block` |
| `firewall` | Zone/rule edits | `get_zones`, `add_rule` |
| `upgrade` | Firmware up/downgrade | `start`, `check`, `get_progress` |

Trace the Vue bundle for the matching UI section to get the exact method names and param shapes for any module not listed.

---

## Reusable bash helper

A minimal client that handles login, sid caching, and one-shot retry on session expiry:

```bash
#!/usr/bin/env bash
set -euo pipefail
RPC=${RPC:-http://192.168.8.1/rpc}
PASS_FILE=${PASS_FILE:-$HOME/.glinet-pass}    # mode 600
SID_FILE=${SID_FILE:-/tmp/.glinet.sid}

post() { curl -sS -m 10 -X POST "$RPC" -H 'Content-Type: application/json' -d "$1"; }

login() {
  local pw nonce salt resp crypted hash sid
  pw=$(head -1 "$PASS_FILE")
  resp=$(post '{"jsonrpc":"2.0","id":1,"method":"challenge","params":{"username":"root"}}')
  nonce=$(jq -r .result.nonce <<<"$resp")
  salt=$(jq  -r .result.salt  <<<"$resp")
  crypted=$(openssl passwd -5 -salt "$salt" "$pw")
  hash=$(printf '%s:%s:%s' root "$crypted" "$nonce" | sha256sum | awk '{print $1}')
  resp=$(post "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"login\",\"params\":{\"username\":\"root\",\"hash\":\"$hash\"}}")
  sid=$(jq -r .result.sid <<<"$resp")
  [[ -z "$sid" || "$sid" == null ]] && { echo "login failed: $resp" >&2; return 1; }
  printf '%s' "$sid" > "$SID_FILE"; chmod 600 "$SID_FILE"
  echo "$sid"
}

call() {
  local mod=$1 method=$2 params="${3:-}"
  [[ -z "$params" ]] && params='{}'
  local sid; sid=$([[ -s $SID_FILE ]] && cat "$SID_FILE" || login)
  local body resp
  body=$(jq -nc --arg sid "$sid" --arg m "$mod" --arg me "$method" --argjson p "$params" \
    '{jsonrpc:"2.0",id:3,method:"call",params:[$sid,$m,$me,$p]}')
  resp=$(post "$body")
  if jq -e '.error.message=="Access denied"' <<<"$resp" >/dev/null; then
    sid=$(login)
    body=$(jq -nc --arg sid "$sid" --arg m "$mod" --arg me "$method" --argjson p "$params" \
      '{jsonrpc:"2.0",id:3,method:"call",params:[$sid,$m,$me,$p]}')
    resp=$(post "$body")
  fi
  printf '%s' "$resp"
}

case "${1:-}" in
  login) login;;
  call)  shift; call "$@";;
  *) echo "usage: $0 {login|call <mod> <method> [params-json]}" >&2; exit 2;;
esac
```

Save as `glinet-rpc.sh`, `chmod +x`, drop the admin password (single line, no trailing whitespace) in `~/.glinet-pass` (`chmod 600`). Then:

```bash
glinet-rpc.sh call system get_info '{}'
glinet-rpc.sh call wg-server get_status '{}'
glinet-rpc.sh call clients get_list '{}'
```

---

## Pitfalls

- **Empty-string fields are rejected for some methods.** Send `{"name":"foo"}` instead of `{"name":"foo","dns":"","allowed_ips":""}`. The latter returns `Invalid params (-32602)`. Omit fields you don't have a value for; the server applies defaults.
- **Numbers must be JSON numbers**, not strings. `mtu: 1280`, not `mtu: "1280"`. Watch out for `jq --arg` (always strings) vs `jq --argjson` (parses JSON).
- **`call` requires a non-empty fourth param object**. If a method takes no arguments, send `{}`, not `null` or omitted.
- **The `id` in the response echoes the request id**, but it's not validated server-side — clients can use any positive integer. Treat it as a correlation token only.
- **Successful "do nothing" responses are `result: []`** (empty array). Don't assume `result` is always an object.
- **Some compound operations regenerate state.** Adding the first WG peer to a freshly-generated server config replaces the server keypair (because `initialization=true` flips to `false`). Always re-read state after the first write.
- **Session timeout is silent.** A long-running script without keepalives will surprise-fail with `Access denied`. The helper above retries once; for very long jobs, refresh the sid every few minutes.
- **`oui-httpd` is fronted by nginx on some firmware builds.** A malformed body (e.g., from a buggy jq command) can yield an HTML 500 from nginx instead of a JSON-RPC error. Always validate the body before posting if you're scripting in a hurry.
