# GL-iNet Slate 7 — Hardware and Features

## Table of Contents
- [Hardware Specifications](#hardware-specifications)
- [Physical Layout](#physical-layout)
- [Touchscreen Interface](#touchscreen-interface)
- [Wi-Fi Specifications](#wi-fi-specifications)
- [Key Software Features](#key-software-features)
- [Network Modes](#network-modes)
- [Feature Interactions and Limitations](#feature-interactions-and-limitations)

---

## Hardware Specifications

| Component | Detail |
|-----------|--------|
| CPU | Qualcomm quad-core @ 1.1 GHz |
| RAM | 1 GB DDR4 |
| Flash storage | 512 MB NAND |
| Operating system | OpenWrt 23.05, Linux kernel 5.4 |
| Dimensions | 130 × 91 × 34 mm |
| Weight | ~295 g |
| Cooling | Passive (fanless) |
| Operating temperature | 0–40 °C |
| Design recognition | Red Dot Design Award 2025 |

**Power:**
- Input: USB-C with Power Delivery (PD)
- Supported: 5V/3A, 9V/3A, 12V/2.5A
- Maximum consumption: under 18 W (excluding USB devices)
- Included adapter ships with EU, UK, and AU interchangeable plug heads
- Compatible with quality USB-C PD laptop chargers and power banks; avoid low-quality non-PD chargers

---

## Physical Layout

### Rear Panel (all ports)
| Port | Speed | Purpose |
|------|-------|---------|
| WAN Ethernet | 2.5 Gbps (auto-negotiates 10/100/1000/2500) | Uplink from modem or upstream router |
| LAN Ethernet | 2.5 Gbps (auto-negotiates) | Wired client or secondary router |
| USB 3.0 Type-A | USB 3.0 | Tethering, cellular modem, storage |
| USB-C | — | Power input only |

### Left Side
- **Toggle button** — physical switch; fully configurable via Admin Panel → System → Toggle Button Settings; assignable to: toggle VPN on/off, toggle Wi-Fi, or custom actions

### Recessed Reset Button
Dual-function based on touchscreen-guided release:

| Touchscreen Prompt | Action on Release | Effect |
|-------------------|-------------------|--------|
| "Release to Repair Mode" | Release button | Soft reset — restores network/WAN defaults; preserves Wi-Fi credentials, VPN configs, admin password, plugins; re-enables Wi-Fi if disabled |
| "Release to Reset Mode" | Release button | Full factory reset — erases all data and settings |

**Important:** Press the reset button only after the router has fully booted. Pressing during early boot may enter U-Boot failsafe mode unintentionally.

### External Antennas
- 2 × foldable external antennas
- Fold flat for transport; unfold for optimal signal
- Estimated indoor coverage: ~1,500 sq ft (139 m²)

---

## Touchscreen Interface

The touchscreen on the front face is the primary status display and allows basic controls without opening a browser.

### Horizontal Swipe — Status Screens (left/right)
Swipe left or right to cycle through:
1. **Network status** — active WAN type icon (Ethernet, Wi-Fi Repeater, Tethering, Cellular) with color coding
2. **Wi-Fi info** — current SSID, password (partially masked), and QR code for connecting new devices
3. **OpenVPN status** — connection state, provider name, real-time throughput
4. **WireGuard status** — connection state, provider/profile name, real-time throughput
5. **AdGuard Home** — on/off, blocked query count
6. **Tor** — on/off
7. **Traffic statistics** — real-time upload and download speeds
8. **CPU overview** — load percentage, temperature
9. **Clock** — current time

### Vertical Swipe — System Controls (top/bottom)
Swipe down from top:
- **Reboot** the router
- **Lock** the screen

### Interactive Controls on Touchscreen
- Tap VPN status screen to toggle the active VPN tunnel on/off
- Tap Wi-Fi QR screen to let nearby devices scan and connect
- Brightness and auto-lock delay configured via Admin Panel → System → Display Management
- Optional screen lock passcode set in Display Management

---

## Wi-Fi Specifications

| Parameter | 2.4 GHz | 5 GHz |
|-----------|---------|-------|
| Standard | 802.11b/g/n/ax/be | 802.11a/n/ac/ax/be |
| Max throughput | 688 Mbps | 2,882 Mbps |
| Combined (marketed) | 3,570 Mbps (BE3600) | |
| MIMO streams | 2×2 | 2×2 |

**Wi-Fi 7 (802.11be) features:**
- **MLO (Multi-Link Operation)** — router can use both bands simultaneously for a single client connection, improving speed and reducing latency
- **4K QAM** — higher modulation for increased throughput in good signal conditions
- **Enhanced OFDMA** — more efficient spectrum use with many simultaneous clients
- **Preamble puncturing** — operates around interference on parts of the channel
- Maximum simultaneous client connections: 120+

**Security modes:** WPA2, WPA3, WPA2/WPA3 mixed (both bands)

**Default SSIDs:** Printed on the bottom label. Format is `GL-BE3600-XXX` (2.4 GHz) and `GL-BE3600-XXX-5G` (5 GHz) where XXX is a device-specific suffix. The default Wi-Fi password is also on the label.

---

## Key Software Features

### VPN Client
- **WireGuard client** — up to ~490 Mbps measured throughput; hardware-accelerated
- **OpenVPN client with DCO** — up to ~385 Mbps (Data Channel Offload enabled by default)
- **30+ provider integrations** with direct login (no manual file download needed):
  - NordVPN, Mullvad, Surfshark, IPVanish, PIA, PureVPN, Hide.me, AzireVPN, Windscribe, and others
  - NordVPN requires generating an Access Token from the Nord account dashboard (not the regular login password)
- **Manual config upload** for any provider: supports `.conf`, `.ovpn`, `.zip`, `.tar`, `.gz`, `.txt`
- **VPN Kill Switch** — enabled by default when a VPN tunnel is active; blocks internet if the tunnel drops
- **Enhanced Kill Switch** (firmware v4.8+) — blocks ALL non-VPN traffic when policy mode is active
- **Split tunneling (VPN Policies)** — per-device rules: route through VPN, bypass VPN, or default
- **VPN Dashboard** — unified view of all tunnels with real-time status and traffic statistics

### VPN Server
- **WireGuard Server** — generate server config, create named client profiles, export QR code or `.conf` file
- **OpenVPN Server** — TUN (routed) or TAP-S2S (bridged); certificate or username/password authentication
- Can run as VPN client and server simultaneously (e.g., connected to NordVPN while hosting WireGuard for remote access)
- Multi-hop / VPN chaining supported

### AdGuard Home
- Pre-installed — no extra setup to activate; toggle on and it starts blocking immediately
- DNS-based: blocks ads and trackers for every device on the network
- Accessible via Admin Panel → Applications → AdGuard Home; includes its own web interface for filter customization
- Status visible and togglable from the touchscreen

### Tor
- Full-tunnel Tor routing for all connected devices
- Toggle via Admin Panel → VPN → Tor
- **Mutually exclusive** with VPN clients, AdGuard Home, DNS encryption, and IPv6 (all disabled when Tor is active)

### Repeater (WISP mode)
- Connects to upstream Wi-Fi network; rebroadcasts under your own SSID
- All connected devices share the upstream internet
- Setup: Admin Panel → Internet → Repeater → Connect → select upstream SSID → enter password → Apply
- Useful for hotel rooms, cafes, airports where only Wi-Fi uplink is available

### 4G/5G Tethering and Cellular
- **USB tethering** — Android or iOS smartphone via USB cable to the USB 3.0 port
- **USB modem** — 4G/5G dongle plugged into USB 3.0 port for direct cellular data
- **Cellular mode** — separate from Tethering; configured via Admin Panel → Internet → Cellular
- Tethering status shown on touchscreen with color-coded indicator

### Multi-WAN Failover
- Multiple simultaneous WAN connections (e.g., Ethernet primary + Repeater backup + Cellular fallback)
- Automatic failover when primary WAN fails; manual priority ordering
- Load balancing option available
- Configured via Admin Panel → Network → Multi-WAN

### Tailscale
- Built-in integration (beta in firmware 4.x)
- Toggle on in Admin Panel → Applications → Tailscale → follow device bind link to authenticate
- Options: Allow Remote Access WAN, Allow Remote Access LAN, Exit Node
- **Conflict warning:** Do not run simultaneously with WireGuard Client, OpenVPN Client, ZeroTier, GoodCloud Site-to-Site, or AstroWarp — routing conflicts result

### Drop-in Gateway
- Places the Slate 7 inline between main router and network without replacing main router configuration
- Enables VPN client, AdGuard Home, DNS encryption for all devices behind the main router
- Configured via Admin Panel → Network → Network Mode → Drop-in Gateway

### Additional Applications
| Feature | Access Path | Notes |
|---------|-------------|-------|
| Dynamic DNS (DDNS) | Applications → Dynamic DNS | Provides stable `*.glddns.com` hostname tracking your public IP; essential for VPN server with dynamic ISP IP |
| ZeroTier | Applications → ZeroTier | Software-defined virtual LAN; connects devices across different physical networks |
| Network Storage | Applications → Network Storage | USB drive Samba/NAS sharing across local network |
| Parental Controls | Applications → Parental Control | Per-device screen time scheduling and content filtering |
| eSIM Management | Applications → eSIM Management | Manage embedded SIM profiles for cellular connectivity |
| GoodCloud | Cloud → GoodCloud | GL.iNet remote management; optional; fleet management for multiple routers |
| AstroWarp | Cloud → AstroWarp | SD-WAN remote access; alternative to public IP for VPN server |
| Plugins / OpenWrt Packages | Applications → Plugins | Full opkg package ecosystem |
| LuCI (full OpenWrt UI) | System → Advanced Settings | Complete OpenWrt web interface for advanced configuration |

### DNS Encryption
- DNS over HTTPS (DoH) and DNS over TLS (DoT) supported
- Configure upstream servers (Cloudflare, Google, NextDNS, or custom)
- Admin Panel → Network → DNS

### WPA3, IPv6, IGMP Snooping, NAT Tuning
- WPA3 supported on both bands
- IPv6 configurable via Admin Panel → Network → IPv6
- IGMP Snooping for IPTV/multicast: Admin Panel → Network → IGMP Snooping
- Full Cone NAT toggle, SIP ALG toggle: Admin Panel → Network → NAT Settings
- Hardware NAT acceleration toggle: Admin Panel → Network → Network Acceleration

---

## Network Modes

Select via Admin Panel → Network → Network Mode.

### Router Mode (default)
- Standard NAT gateway between WAN and LAN
- DHCP server active; all features fully available
- Admin panel always accessible at `192.168.8.1`
- Use when: primary router in hotel, home, or office

### Access Point (AP) Mode
- Connects to upstream router via Ethernet WAN port
- NAT and DHCP disabled; all devices get IPs from upstream DHCP
- Admin panel IP changes to whatever upstream DHCP assigns — find it in upstream router's client list
- Most GL.iNet features (VPN, AdGuard, firewall) not functional
- Use when: adding wireless coverage to an existing wired network

### Extender Mode
- Wirelessly connects to upstream Wi-Fi and rebroadcasts under a new SSID
- Admin panel still accessible at `192.168.8.1`
- Throughput penalty: radio must receive and retransmit on same frequency (~50% bandwidth reduction)
- Use when: Wi-Fi range extension is needed and no Ethernet run is possible

### WDS Mode
- Wireless bridge between compatible routers; single subnet across all access points
- Admin panel IP changes (same caveat as AP mode)
- Requires upstream router to support WDS
- Use when: multi-floor/campus coverage with a single flat network

### Drop-in Gateway Mode
- Sits inline between main router and network; transparent pass-through
- Adds VPN and AdGuard to entire network without changing main router
- Admin panel accessible at the Slate 7's own IP
- Use when: cannot replace main router but want network-wide VPN/ad blocking

### Recovering After Mode Switch
If the admin panel becomes unreachable (AP/WDS mode):
- Option A: Find the assigned IP from the upstream router's DHCP table
- Option B: Hold reset button until touchscreen shows "Release to Repair Mode" — this reverts to Router Mode

---

## Feature Interactions and Limitations

| Limitation | Detail |
|-----------|--------|
| Tor disables other features | When Tor is active: VPN clients, AdGuard Home, DNS encryption, and IPv6 are all disabled |
| Hardware acceleration vs. traffic graphs | Enabling hardware NAT acceleration disables real-time traffic statistics display |
| Tailscale conflicts | Do not combine with WireGuard Client, OpenVPN Client, ZeroTier, GoodCloud Site-to-Site, or AstroWarp |
| VPN Server requires public IP | WireGuard/OpenVPN server needs a public IP from ISP; CGNAT blocks incoming connections — use AstroWarp as workaround |
| AP/WDS mode loses admin at default IP | Must locate new DHCP-assigned IP from upstream router, or soft-reset to Router Mode |
| Repeater mode stability | Some firmware versions (notably 4.7.1) have intermittent Repeater connectivity issues; may need multiple connection attempts |
| Kernel version | Kernel 5.4.x is mature but older; may limit compatibility with very new hardware drivers |
