# Linux WG client + overlay VPNs (stacked tunnels)

Patterns for running a Linux WireGuard client against a GL-iNet sdk4 WG server with full-tunnel egress, then layering a mesh overlay (Tailscale, ZeroTier) on top so overlay traffic still rides inside the outer WG. Includes the policy-routing fixes that nested tunnels need on Linux. Server-side provisioning lives in `wireguard-server-api.md`; this file covers what happens on the client.

---

## Client-side setup against a GL-iNet WG server

The client config returned by `wg-server.generate_peer` is almost ready as `/etc/wireguard/wg0.conf`. Two things to set explicitly:

```ini
[Interface]
Address    = 10.1.0.2/24, fd00:.../64       # from generate_peer.address
PrivateKey = <generate_peer.private_key>
DNS        = 10.1.0.1, fd00:...:1            # from generate_peer.dns
MTU        = 1280                             # see MTU section below

[Peer]
PublicKey           = <generate_peer.public_key>      # server's public key
PresharedKey        = <generate_peer.presharedkey>
AllowedIPs          = 0.0.0.0/0, ::/0                  # full-tunnel kill-switch shape
Endpoint            = 192.168.8.1:51820                # LAN IP for local-only; public IP/DDNS otherwise
PersistentKeepalive = 25
```

Bring up and persist:

```bash
sudo apt-get install -y wireguard-tools         # kernel module ships with stock Ubuntu/Debian
sudo install -m 600 wg0.conf /etc/wireguard/    # mode 600 is enforced by wg-quick
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0              # auto-up on boot
```

Verify the tunnel is alive:

```bash
sudo wg show wg0                                # 'latest handshake' should show recent activity
ip route get 1.1.1.1                            # should resolve via wg0 in table 51820
curl -s https://ifconfig.me                     # should report the WG server's WAN IP
```

GL-iNet specifics on the server side: the kernel interface is `wgserver` (not `wg0`), and the `local_access` setting must be `true` for clients to reach the server's LAN through the tunnel. See `wireguard-server-api.md`.

---

## What `wg-quick` actually does for full-tunnel `AllowedIPs`

When `AllowedIPs` includes `0.0.0.0/0` (and/or `::/0`), `wg-quick` installs a more elaborate routing setup than a simple default route:

```
Table 51820 (created):
  0.0.0.0/0 dev wg0
  ::/0     dev wg0

ip rules (added):
  5208  from all lookup main suppress_prefixlength 0   # main table for non-default prefixes only
  5209  not from all fwmark 0xca6c lookup 51820        # everything without WG's own fwmark → wg0
```

The `fwmark 0xca6c` (= 51820 decimal) is set on wg0's own egress UDP socket (`wg show wg0` displays it). Rule 5209 says "if the packet does not have that mark, route via wg0", which sends *application* traffic into the tunnel while letting the *encrypted* WG handshake/data packets fall through to the main table and reach the underlying NIC. This is the standard wg-quick policy-routing kill-switch — it preserves a single egress shape (UDP to the server endpoint) even if `AllowedIPs` is broader than the default route.

If wg0 goes down, the rules persist briefly (until `PreDown` runs); routes in table 51820 still match but transmission fails — the client loses connectivity rather than leaking. A graceful failure mode.

---

## MTU when stacking tunnels

WireGuard adds ~80 bytes of overhead (32 WG header + 8 UDP + 20–40 IP + 16 auth tag). Default tun MTU is 1420.

In a stacked setup (overlay-VPN-over-WG, or WG-over-Wi-Fi-bridged-VM, etc.), the inner tunnel's MTU must fit inside the outer tunnel's payload. Conservative choice:

| Underlying path | Recommended client `MTU` | Rationale |
|-----------------|--------------------------|-----------|
| Direct Ethernet, 1500 path | `1420` (default) | One layer of encapsulation |
| Wi-Fi to a GL-iNet device | `1380` | Wi-Fi MTU surprises plus encapsulation |
| WG client behind another NAT'd VM/container guest network | `1280` | Two hops of NAT/encap, conservative |
| Inner overlay (Tailscale) on top of a WG client | tailscale tun ≤ `1200` | WG already takes ~80; overlay also adds ~80 |

Symptoms of an MTU mismatch on a stacked tunnel:
- TSMP / small UDP probes work, large TCP transfers stall or hang on first DATA packet
- `tailscale netcheck` reports `UDP: false`
- `wg show` shows transfer counters incrementing slowly or unevenly
- ICMP `ping -s 1400` to a peer succeeds, `-s 1500` does not

Fix: lower the inner tunnel MTU. For Tailscale: `sudo ip link set dev tailscale0 mtu <n>`; persist with a oneshot systemd unit or by running it from the WG client's `PostUp`.

---

## Layering Tailscale on a WG client tunnel

Tailscale running on a host with a full-tunnel WG client is a common stack: the WG link gives a single defined egress shape; Tailscale adds reachability into a private overlay. Done naively, two things go wrong simultaneously.

### Problem 1 — Tailscale's `fwmark` bypass leaks to the underlying NIC

Tailscale stamps `fwmark 0x80000` on its UDP sockets (verify with `ss -lunpe | grep tailscaled`) and installs ip rules at priorities 5210/5230/5250:

```
5210  from all fwmark 0x80000/0xff0000 lookup main
5230  from all fwmark 0x80000/0xff0000 lookup default
5250  from all fwmark 0x80000/0xff0000 unreachable
```

This bypass is defensive: it prevents Tailscale's own encrypted traffic from looping through `tailscale0`. It is interface-agnostic, so when `wg0` is the default route, those rules send marked packets out the *underlying* NIC instead — Tailscale's STUN probes, DERP TLS, and direct-peer UDP all leak around `wg0`.

The fix is a higher-priority rule (lower number) that captures the same fwmark and sends it to wg0's table:

```
5200  from all fwmark 0x80000/0xff0000 lookup 51820
```

Result: marked traffic goes via wg0 first, gets encrypted, leaves as the same outer UDP shape as everything else. Tailscale falls back to DERP cleanly when direct UDP probes can't be answered through the double-NAT — the DERP TCP/443 connections are sourced from the WG tunnel IP and ride wg0.

### Problem 2 — wg-quick's catch-all shadows the tailnet route

wg-quick's rule at priority 5209 (`not fwmark 0xca6c lookup 51820`) sends *all* unmarked egress through wg0 — including packets destined for `100.64.0.0/10`, the tailnet's CGNAT range. Tailscale's specific `/32` routes for each peer live in table 52 (consulted at priority 5270), but 5209 fires first, so the kernel sends them out wg0 and `tailscale0` never sees them. ICMP and TCP to mesh peers time out; only TSMP (which goes through Tailscale's userspace directly, not the kernel route) appears to work.

The fix is two destination-based rules at higher priority than 5209 that send the tailnet ranges directly to Tailscale's routing table:

```
5205  from all to 100.64.0.0/10        lookup 52   # IPv4 CGNAT range
5206  from all to 100.100.100.100/32   lookup 52   # MagicDNS resolver
5205  from all to fd7a:115c:a1e0::/48  lookup 52   # IPv6 ULA range (ip -6 rule)
```

This does *not* leak: traffic enters `tailscale0`, Tailscale userspace encrypts it, sends it as UDP from a fwmark-0x80000 socket, hits rule 5200 above, and gets re-encapsulated through wg0.

### Putting it in `wg0.conf`

Both fixes are idempotent and belong in `wg-quick`'s `PostUp` / `PreDown`:

```ini
[Interface]
# ... Address, PrivateKey, DNS, MTU ...

# Tailscale fwmark passthrough (overrides Tailscale's own bypass to wg0):
PostUp  = ip    rule add priority 5200 fwmark 0x80000/0xff0000 lookup 51820 || true
PostUp  = ip -6 rule add priority 5200 fwmark 0x80000/0xff0000 lookup 51820 || true
PreDown = ip    rule del priority 5200 fwmark 0x80000/0xff0000 lookup 51820 || true
PreDown = ip -6 rule del priority 5200 fwmark 0x80000/0xff0000 lookup 51820 || true

# Tailnet route precedence (overrides wg-quick's 5209 catch-all for 100.64/10):
PostUp  = ip    rule add priority 5205 to 100.64.0.0/10        lookup 52 || true
PostUp  = ip    rule add priority 5206 to 100.100.100.100/32   lookup 52 || true
PostUp  = ip -6 rule add priority 5205 to fd7a:115c:a1e0::/48  lookup 52 || true
PreDown = ip    rule del priority 5205 to 100.64.0.0/10        lookup 52 || true
PreDown = ip    rule del priority 5206 to 100.100.100.100/32   lookup 52 || true
PreDown = ip -6 rule del priority 5205 to fd7a:115c:a1e0::/48  lookup 52 || true
```

`PostUp` runs after wg-quick installs its own rules, so the priority numbers are stable. `PreDown` removes them before the tunnel goes down so the system returns to its pre-stack state.

After editing, cycle `wg-quick@wg0` and restart `tailscaled` so its sockets reopen under the new rules:

```bash
sudo systemctl restart wg-quick@wg0
sudo systemctl restart tailscaled
```

### Final ip-rule layout for a working Tailscale-over-WG stack

```
0     from all lookup local                                 # kernel
5200  from all fwmark 0x80000/0xff0000 lookup 51820         # OURS — Tailscale → wg0
5205  from all to 100.64.0.0/10        lookup 52            # OURS — tailnet → tailscale0
5206  from all to 100.100.100.100      lookup 52            # OURS — MagicDNS → tailscale0
5208  from all lookup main suppress_prefixlength 0          # wg-quick
5209  not from all fwmark 0xca6c lookup 51820               # wg-quick — catch-all → wg0
5210  from all fwmark 0x80000/0xff0000 lookup main          # Tailscale (now shadowed by 5200)
5230  from all fwmark 0x80000/0xff0000 lookup default       # Tailscale (now shadowed)
5250  from all fwmark 0x80000/0xff0000 unreachable          # Tailscale (now shadowed)
5270  from all lookup 52                                    # Tailscale general (now shadowed by 5205/5206)
32766 from all lookup main
32767 from all lookup default
```

Lower priority numbers are evaluated first; "shadowed" rules never match because a higher-priority rule already routed the packet.

---

## Verification: leak check and reachability

A single recipe to prove the stack is correct.

```bash
# 1. Start a tcpdump that EXCLUDES the outer WG, ARP/ICMPv6, the host's
#    inbound SSH (or whatever management plane reaches the box), and DNS
#    to the host. Anything captured by this filter is a leak.
sudo timeout 10 tcpdump -i <underlay-NIC> -n \
  'not (udp port 51820 and host <wg-server-LAN-IP>)
   and not arp and not icmp6
   and not (host <host-mgmt-IP> and tcp port 22)
   and not (host <host-mgmt-IP> and udp port 53)' &

# 2. Generate a representative traffic mix in another shell:
#    - mesh ICMP and TCP (ping/ssh to a tailnet peer)
#    - public-internet TCP (curl to ifconfig.me)
#    - DNS lookups
ping  -c 2 -W 2 100.64.0.<peer> >/dev/null
ssh   -o BatchMode=yes user@100.64.0.<peer> 'true'
curl  -s -m 3 https://ifconfig.me >/dev/null
nslookup example.com >/dev/null

wait
```

Expected: the tcpdump captures **zero packets**. If anything appears, identify the offending source/destination, then check `ip route get <dest> mark <fwmark>` and `ss -anpe` to find the originating socket and its fwmark.

`curl -s https://ifconfig.me` should report the WG server's WAN IP (the public IP visible from the outside is the server's, not the client's). `tailscale ping <peer>` should succeed. `ssh user@<peer-tailnet-IP>` should connect.

---

## Diagnostic recipes

| Symptom | Command | What it tells you |
|---------|---------|-------------------|
| What route does a packet take? | `ip route get <dest>` | The actual selected route. Add `mark <fwmark>` to simulate Tailscale-marked traffic. Add `from <src>` to simulate a specific source IP. |
| What sockets are on the underlay? | `ss -tunpe` | Per-process socket list including `fwmark`. Filter by `grep tailscaled` to see which Tailscale sockets carry which marks. |
| Are tailnet routes alive? | `ip route show table 52` | Tailscale's per-peer `/32` routes; one entry per online peer. |
| Are direct paths working? | `tailscale ping <peer>` (default) | Tries direct first, falls back to DERP. The output line ends with `via 1.2.3.4:port` (direct) or `via DERP(<region>)` (relay). |
| Is the relay working? | `tailscale ping --until-direct=false <peer>` | Forces DERP path; useful to confirm DERP works while direct does not. |
| Is Tailscale's own protocol working? | `tailscale ping --tsmp <peer>` | Bypasses kernel routing for the test; isolates Tailscale dataplane health from policy-routing problems. |
| Did Tailscale's MagicSock pick a path? | `sudo journalctl -u tailscaled -f` | Look for `disco: node [...] now using <ip>:<port> mtu=<n>`. The `mtu` value shows the path MTU Tailscale chose; if larger than the outer wg0 MTU, expect drops. |
| Is the outer tunnel handshaking? | `sudo wg show wg0` | `latest handshake: <recent>` and growing transfer counters. No handshake = peer can't reach the server endpoint. |
| Why does ICMP fail when TCP works? | `ip route get <dest>` for both | Often reveals different tables matched (e.g., 51820 vs 52). The route table is the routing decision regardless of L4 protocol — it shouldn't differ by protocol unless rules are using `ipproto`/`sport`/`dport` matchers. |

---

## Other overlay VPNs

The fwmark-bypass and route-shadowing patterns generalize to anything that installs its own ip rules:

- **Tailscale**: fwmark `0x80000/0xff0000`, table `52`, peer range `100.64.0.0/10` + MagicDNS `100.100.100.100`, IPv6 ULA `fd7a:115c:a1e0::/48`.
- **headscale-managed nodes**: same as Tailscale (it is the same client).
- **ZeroTier**: does not install ip rules in default config (uses a tun device with conventional routes); usually needs no policy-routing fix to layer over WG. Confirm with `ip rule` after starting `zerotier-one`.
- **Nebula**: uses `nebula1` tun, conventional routes, no fwmark by default.
- **OpenVPN**: conventional default-route or specific routes; if it pushes a default route, it will conflict with wg-quick's catch-all — typically you choose one or the other as the "outer" tunnel.

The general approach for any overlay-on-WG stack:

1. Bring up the outer WG with full-tunnel `AllowedIPs`.
2. Install the overlay; observe `ip rule` and `ip route show table all`.
3. Identify (a) any *fwmark-based bypass* that escapes to the underlay, (b) any *destination prefixes* the overlay routes that are shadowed by wg-quick's 5209 catch-all.
4. Insert higher-priority rules at 5200-range that re-direct (a) into wg0's table 51820 and (b) into the overlay's table.
5. Verify with the leak-check recipe above and reachability checks (overlay ping + ssh).
