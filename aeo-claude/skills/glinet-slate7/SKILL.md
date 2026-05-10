---
name: glinet-slate7
description: |
  Comprehensive reference for the GL-iNet Slate 7 travel router (model GL-BE3600, Wi-Fi 7).
  Covers hardware specs, 2.5G ports, touchscreen interface, full admin panel menu structure,
  VPN client setup (WireGuard/OpenVPN; NordVPN, Mullvad, Surfshark, and 30+ providers),
  WireGuard/OpenVPN server setup, AdGuard Home, Tor, Tailscale, DDNS, network modes
  (Router/AP/Extender/WDS/Drop-in Gateway), SSH/CLI access with command reference,
  factory reset, firmware update, and U-Boot bricked-device recovery.
  Use when a user specifically asks about the GL-iNet Slate 7 or GL-BE3600 — setup,
  initial connection, admin panel access, VPN configuration, SSH, troubleshooting lost
  admin access, or device recovery. Do not trigger for generic router questions not
  specific to GL-iNet Slate 7.
---

# GL-iNet Slate 7 (GL-BE3600) Reference

---

## Quick Reference

| Item | Value |
|------|-------|
| Model | GL-BE3600 (Slate 7) |
| Admin panel URL | `http://192.168.8.1` |
| Default LAN subnet | `192.168.8.0/24` |
| Default 2.4 GHz SSID | `GL-BE3600-XXX` (see bottom label) |
| Default 5 GHz SSID | `GL-BE3600-XXX-5G` (see bottom label) |
| Default Wi-Fi password | Printed on bottom label |
| Admin password | None — must be set on first boot |
| SSH username / port | `root` / `22` |
| SSH password | Same as admin password |
| U-Boot recovery IP | Computer: `192.168.1.2` → Router: `192.168.1.1` |
| Soft reset (Repair Mode) | Hold reset until touchscreen shows "Release to Repair Mode" |
| Factory reset | Hold reset until touchscreen shows "Release to Reset Mode" |
| Firmware downloads | `https://dl.gl-inet.com/router/be3600/` |
| Official docs | `https://docs.gl-inet.com/router/en/4/user_guide/gl-be3600/` |

---

## What This Router Does

The Slate 7 is purpose-built for three scenarios:

1. **Privacy on the go** — connects to hotel/cafe Wi-Fi or cellular data, then presents a clean, VPN-protected network to all your devices
2. **Portable gateway** — acts as a full NAT router with firewall, DHCP, and DNS for any location
3. **Remote access hub** — runs WireGuard or OpenVPN server so you can reach your home network securely from anywhere

---

## Key Capabilities at a Glance

- **Wi-Fi 7 (802.11be)** with MLO — up to 3,570 Mbps theoretical, 2.4 GHz + 5 GHz simultaneously
- **2.5 Gbps WAN + 2.5 Gbps LAN** Ethernet ports
- **WireGuard client** up to ~490 Mbps throughput; **OpenVPN with DCO** up to ~385 Mbps
- **30+ VPN provider integrations** (NordVPN, Mullvad, Surfshark, PIA, and more)
- **VPN Server** (WireGuard + OpenVPN) with client config export
- **AdGuard Home** — DNS-level ad/tracker blocking, pre-installed (disabled when Tor is active)
- **Tor** — full-tunnel Tor routing for all connected devices (mutually exclusive with VPN clients, AdGuard Home, DNS encryption, and IPv6)
- **Tailscale** and **ZeroTier** overlay networking
- **Multi-WAN failover** — Ethernet + Repeater + Cellular with automatic switchover
- **Drop-in Gateway mode** — extend any existing router with VPN and ad blocking
- **Touchscreen** — swipe through status screens; toggle VPN and view Wi-Fi QR code without a browser; physical side toggle button assignable via System → Toggle Button Settings
- **USB 3.0** — smartphone tethering, 4G/5G dongle, or network-attached storage
- **LuCI (full OpenWrt UI)** accessible via Admin Panel → System → Advanced Settings

---

## Reference Files

| File | Contents |
|------|----------|
| [hardware-and-features.md](hardware-and-features.md) | Hardware specs, ports, buttons, touchscreen screens, LED behavior, network modes comparison, feature limitations and known issues |
| [web-ui-guide.md](web-ui-guide.md) | Admin panel menu structure, every section explained, VPN setup flows (WireGuard client/server, OpenVPN client/server), AdGuard, DDNS, Tailscale, Tor, Multi-WAN |
| [setup-and-management.md](setup-and-management.md) | Initial connection and first-time setup wizard, direct connection (no internet), SSH/CLI access and useful commands, troubleshooting, firmware update, U-Boot recovery |

---

## Common Tasks

### Get to the admin panel
Connect to the router by Ethernet (LAN port) or Wi-Fi (`GL-BE3600-XXX`), then open `http://192.168.8.1`.

### Connect to a VPN provider
Admin Panel → VPN → WireGuard Client (or OpenVPN Client) → select provider or "Add Manually" → upload config → start. See [web-ui-guide.md](web-ui-guide.md) for provider-specific credential notes.

### Enable ad blocking
Admin Panel → Applications → AdGuard Home → toggle on. Can also be toggled directly from the touchscreen.

### Share Wi-Fi credentials via QR code
Swipe the touchscreen to the Wi-Fi screen — it shows the SSID, password, and a scannable QR code.

### Reset to factory defaults
Hold the reset button until the touchscreen shows **"Release to Reset Mode"**, then release. Or: Admin Panel → System → Reset Firmware → Delete All and Reboot.

### Access CLI
`ssh root@192.168.8.1` — password is the same as your admin panel password. See [setup-and-management.md](setup-and-management.md) for useful commands.

### Run a VPN server (WireGuard)
Admin Panel → VPN → WireGuard Server → Generate Configuration → Profiles tab → Add profile → export QR/config → Start server. Requires a public IP or DDNS hostname. Full flow in [web-ui-guide.md](web-ui-guide.md).

### Router is unreachable at 192.168.8.1
Mode may have been switched to AP or WDS. Hold the reset button until the touchscreen shows "Release to Repair Mode", then release — this reverts to Router Mode. See [setup-and-management.md](setup-and-management.md).

### Device bricked / firmware corrupted
Enter U-Boot recovery mode, set computer IP to `192.168.1.2`, open `http://192.168.1.1`, flash firmware. Full procedure in [setup-and-management.md](setup-and-management.md).

---

## Network Modes Summary

| Mode | NAT/DHCP | Admin at 192.168.8.1 | VPN/Features | Best For |
|------|----------|----------------------|--------------|----------|
| **Router** (default) | Yes | Always | All enabled | Gateway, travel, primary router |
| **Access Point** | No | No — find IP from upstream | Limited | Wired uplink, extend coverage |
| **Extender** | No | Yes | Limited | Wireless range extension |
| **WDS** | No | No — find IP from upstream | Limited | Multi-router bridge |
| **Drop-in Gateway** | Transparent | Yes | VPN + AdGuard for entire upstream network | Augment existing router |

Full mode details and switching instructions: [hardware-and-features.md](hardware-and-features.md)
