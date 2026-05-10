# GL-iNet Slate 7 — Web Admin Panel and Flows

## Table of Contents
- [Accessing the Admin Panel](#accessing-the-admin-panel)
- [Dashboard Overview](#dashboard-overview)
- [Menu Structure Reference](#menu-structure-reference)
- [VPN Client Flows](#vpn-client-flows)
- [VPN Server Flows](#vpn-server-flows)
- [Key Application Setup Flows](#key-application-setup-flows)

---

## Accessing the Admin Panel

**Default URL:** `http://192.168.8.1`

Open from any device connected to the router (wired or Wi-Fi). Chrome, Edge, or Safari recommended.

**Login:** Use the admin password you set during first-time setup. There is no factory default password.

**Alternative access:**
- GL.iNet mobile app (iOS/Android) can manage the router locally and via GoodCloud
- GoodCloud web portal for remote access when the router is online

**If the panel is unreachable:**
- Check you are connected to the router's network, not a different Wi-Fi
- If the router mode was changed (AP, WDS), the IP changed — see [setup-and-management.md](setup-and-management.md) for recovery
- Try `http://192.168.8.1` not `https://` (the panel uses HTTP on the LAN by default)

---

## Dashboard Overview

The main dashboard displays:
- **Connection type icon** — Ethernet, Repeater (Wi-Fi), Tethering, or Cellular; click the active icon to view or change settings for that WAN type
- **Real-time speed** — upload and download Mbps
- **Connected clients count** — tap to jump to Clients list
- **VPN status badge** — active tunnel name and state
- **AdGuard Home status badge** — on/off and blocked query count
- **Quick-access tiles** for all four internet source types

---

## Menu Structure Reference

### INTERNET

| Sub-section | What It Controls |
|-------------|-----------------|
| Ethernet | WAN via wired connection; DHCP auto, static IP, or PPPoE (for DSL); MAC clone |
| Repeater | Scan and connect to upstream Wi-Fi networks (WISP/wireless WAN); manages saved networks |
| Tethering | USB smartphone tethering; Bluetooth tethering |
| Cellular | USB 4G/5G modem management; APN configuration |

### WIRELESS

| Setting | Notes |
|---------|-------|
| 2.4 GHz / 5 GHz enable/disable | Turn bands on or off independently |
| SSID | Network name per band |
| Password | Per-band Wi-Fi password |
| Security mode | WPA2, WPA3, or WPA2/WPA3 mixed |
| Channel | Manual or auto-select |
| Bandwidth | 20/40/80/160/320 MHz depending on band |
| TX power | Low / Medium / High |
| Hidden SSID | Suppress SSID broadcast |
| Randomized BSSID | Privacy feature |
| MLO | Multi-Link Operation (Wi-Fi 7 cross-band bonding) |
| Guest Network | Separate isolated SSID; available per band; guest devices cannot reach main LAN |

### CLIENTS

| Function | Notes |
|----------|-------|
| Connected device list | Shows name, IP, MAC, speed, data usage per device |
| Block / Unblock | Per-device internet access control |
| VPN Policy assignment | Assign each client to: use VPN, bypass VPN, or inherit default |

### VPN

| Sub-section | Notes |
|-------------|-------|
| WireGuard Client | Provider integrations + manual config; multiple server groups |
| WireGuard Server | Server config; named profiles; QR/file export |
| OpenVPN Client | NordVPN integration + manual .ovpn upload |
| OpenVPN Server | TUN or TAP-S2S; cert or username/password auth; client config export |
| Tor | Enable/disable full-tunnel Tor for all clients |
| VPN Dashboard | Unified status view for all tunnels; traffic stats |
| VPN Policies | Global and per-device split tunneling rules; Kill Switch settings |

### APPLICATIONS

| Application | Notes |
|------------|-------|
| Plugins | OpenWrt opkg package installer |
| Dynamic DNS | Enable DDNS for a `*.glddns.com` subdomain tracking public IP |
| Network Storage | USB drive Samba share setup |
| AdGuard Home | Enable/disable; launches AdGuard Home web UI within the router |
| Parental Control | Per-device time schedules and content category filters |
| ZeroTier | Virtual LAN overlay; enter Network ID to join |
| Tailscale | Mesh VPN; device binding; exit node and remote access options |
| eSIM Management | Manage cellular eSIM profiles |

### CLOUD

| Service | Notes |
|---------|-------|
| GoodCloud | GL.iNet remote management platform; optional; enables remote admin panel access |
| AstroWarp | SD-WAN and remote access; useful when ISP uses CGNAT |

### NETWORK

| Sub-section | Notes |
|-------------|-------|
| Firewall | Port forwarding rules; DMZ; custom open ports |
| Multi-WAN | Define multiple WAN interfaces; set priority and failover or load balancing |
| LAN | Change LAN IP / subnet; DHCP range; DHCP lease time; AP isolation |
| Guest Network | Guest SSID settings; isolation from main LAN |
| DNS | Upstream DNS servers; DoH/DoT encryption; custom DNS |
| Ethernet Ports | Port role assignment |
| Network Mode | Switch between Router / AP / Extender / WDS / Drop-in Gateway |
| IPv6 | Enable and configure IPv6 addressing |
| Drop-in Gateway | Inline pass-through mode configuration |
| IGMP Snooping | Multicast optimization for IPTV |
| Network Acceleration | Hardware NAT toggle (disables traffic graphs when enabled) |
| NAT Settings | Full Cone NAT; SIP ALG |
| Port Forwarding | Same rules as Firewall → Port Forwarding |

### SYSTEM

| Sub-section | Notes |
|-------------|-------|
| Overview | CPU load, memory, storage, uptime, firmware version, LED on/off, device info |
| Upgrade | Online OTA check / local firmware file upload |
| Scheduled Tasks | Automate: LED schedule, reboot schedule, Wi-Fi band schedule |
| Display Management | Touchscreen: which status screens appear, brightness, auto-lock delay, passcode |
| Time Zone | Regional time setting |
| Toggle Button Settings | Assign function to the physical side toggle switch |
| Logs | System, kernel, crash, cloud, Nginx logs; export as file |
| Security | Change admin password; enable/disable local or remote admin access |
| Reset Firmware | Factory reset via web UI |
| Advanced Settings | Link to LuCI (full OpenWrt web interface) |

---

## VPN Client Flows

### WireGuard Client — Integrated Provider (NordVPN, Mullvad, Surfshark, etc.)

1. Admin Panel → VPN → WireGuard Client
2. Select your provider from the integration list
3. Enter credentials:
   - **NordVPN:** generate an Access Token from the NordVPN account dashboard (not your regular login password); paste the token
   - **Mullvad:** enter your Mullvad account number
   - **Others:** username + password or API token per provider instructions
4. Click "Save and Continue" — the router fetches server configurations from the provider
5. Browse the server list; click the three-dot menu next to a server → **Start**
6. VPN Dashboard shows a green indicator when connected
7. To configure split tunneling: VPN → VPN Policies

### WireGuard Client — Manual Configuration

1. Download the WireGuard `.conf` file from your VPN provider's portal
2. Admin Panel → VPN → WireGuard Client → **Add Manually**
3. Enter a group name (e.g., `ProtonVPN`)
4. Click "Upload File" and select the `.conf` file, or use "Text Mode" to paste the contents
5. Click Apply
6. Three-dot menu next to the new entry → **Start**

### OpenVPN Client — NordVPN

1. Admin Panel → VPN → OpenVPN Client → NordVPN tab
2. Obtain service credentials from NordVPN account dashboard (separate from Access Token; look for "Service credentials" or "Manual setup" section)
3. Enter username and password; select preferred server regions and protocol
4. The router downloads configuration files automatically
5. Select a server → three-dot menu → **Start**

### OpenVPN Client — Manual Configuration

1. Download `.ovpn` configuration file from your VPN provider
2. Admin Panel → VPN → OpenVPN Client → **Add Manually**
3. Enter a group name
4. Upload the `.ovpn` file
5. Select authentication type:
   - No authentication
   - Username and password only
   - Passphrase only
   - Username, password, and passphrase
6. Enter credentials as required by the provider
7. Click Apply → three-dot menu → **Start**
8. Green indicator in VPN Dashboard confirms connection

### VPN Policies (Split Tunneling)

Admin Panel → VPN → VPN Policies

- **Global default:** set whether "All Other Traffic" goes through VPN or bypasses VPN
- **Per-device rules:** click a device in the client list → assign: "Use VPN", "Don't Use VPN", or "Default"
- **Kill Switch:** enabled by default; blocks internet access if the VPN tunnel drops unexpectedly
- **Enhanced Kill Switch (firmware v4.8+):** when "All Other Traffic" is set to bypass, blocks all unmatched traffic entirely

---

## VPN Server Flows

### WireGuard Server Setup

**Prerequisites:**
- Public IP address from your ISP (check with `https://whatismyip.com` or similar)
- If behind CGNAT (carrier-grade NAT), public connectivity is not available — use AstroWarp or a VPS relay instead
- If the Slate 7 is sub-router (not directly on internet), configure port forwarding on the upstream router: forward **UDP port 51820** to the Slate 7's LAN IP

**Steps:**

1. Admin Panel → VPN → WireGuard Server
2. Click **"Generate Configuration"** (first time only)
3. Review tunnel IP (default `10.0.0.1/24`); if this conflicts with your upstream network range, change to an alternative such as `10.1.0.1/24`
4. Switch to the **Profiles** tab → click **Add** → name the profile (e.g., `Laptop`, `Phone`)
5. Optionally configure the **Route Rules** tab to allow clients to reach LAN devices through the server
6. Click a profile → choose export format:
   - **QR Code** — scan with WireGuard mobile app
   - **Plain Text** — copy/paste into WireGuard desktop app or another router
   - **`.conf` File** — download and import into any WireGuard client
7. When prompted for server address (firmware v4.8+), enter:
   - Your public IP, **or**
   - Your DDNS hostname (strongly recommended if your IP is dynamic — see DDNS setup below)
8. Click **Start** to activate the server
9. Verify: monitor traffic on the WireGuard Server page; from an external connection, check that your visible IP matches the server's public IP

**Enable DDNS for a stable server address:**
Admin Panel → Applications → Dynamic DNS → Enable DDNS → Apply. A hostname in the format `<device-id>.glddns.com` is generated. Use this hostname as the server address when exporting client profiles.

### OpenVPN Server Setup

**Prerequisites:** Same as WireGuard Server (public IP required; forward **UDP port 1194** on upstream router if sub-router)

**Steps:**

1. Admin Panel → VPN → OpenVPN Server
2. Click **"Generate Configuration"**
3. Configure settings:
   - **Device Mode:** `TUN` (routed; most common) or `TAP-S2S` (bridged/site-to-site)
   - **Protocol:** `UDP` (recommended for performance) or `TCP` (for restrictive firewalls)
   - **Authentication:** Certificate only / Username+Password only / Both
4. If using username/password auth: switch to **Users** tab → add user accounts before exporting configs
5. Click **"Export Client Configuration"** → download the `.ovpn` file
   - (firmware v4.8+) Specify server address: public IP, DDNS hostname, or current WAN IP
6. Click **Start** to activate the server
7. Distribute the exported `.ovpn` file to clients; import into any OpenVPN client app

**Optional — Client-to-Client Access:**
Toggle "Client to Client" on the server config page → re-export and redistribute all client configs. Clients can then reach each other's VPN tunnel IPs.

---

## Key Application Setup Flows

### Enable AdGuard Home

1. Admin Panel → Applications → AdGuard Home
2. Toggle the switch to **On**
3. Click the AdGuard Home link to open its own web UI for custom filter lists, query logs, and statistics
4. Status and quick toggle also available on the touchscreen

### Enable Dynamic DNS (DDNS)

1. Admin Panel → Applications → Dynamic DNS
2. Toggle **"Enable DDNS"** → click Apply
3. The assigned hostname (e.g., `abc123.glddns.com`) appears — copy it
4. Use this hostname as the server address in VPN client configs so clients always find your server even when your ISP changes your IP

### Set Up Tailscale

1. Admin Panel → Applications → Tailscale
2. Toggle **On** → a device bind link appears
3. Open the link in a browser → log into your Tailscale account → authorize the device
4. Configure options:
   - **Allow Remote Access WAN** — reach devices upstream of this router
   - **Allow Remote Access LAN** — access devices on this router's LAN network
   - **Exit Node** — route all your internet traffic through a Tailscale exit node you own
5. Check Tailscale admin console (`https://login.tailscale.com/admin/machines`) to confirm the router appears
6. Avoid running simultaneously with WireGuard Client, OpenVPN Client, ZeroTier, GoodCloud Site-to-Site, or AstroWarp

### Set Up Multi-WAN Failover

1. Admin Panel → Network → Multi-WAN
2. Add WAN interfaces (e.g., Ethernet as primary; Repeater as secondary; Cellular as tertiary)
3. Set priority order by drag-and-drop or up/down arrows
4. Choose policy: **Failover** (uses lowest-priority backup only when primary fails) or **Load Balancing**
5. Configure health check method (ping to a public IP like `8.8.8.8`) and interval
6. Click Apply

### Switch Network Mode

1. Admin Panel → Network → Network Mode
2. Select the target mode
3. Read the warning dialog (some modes change admin panel accessibility)
4. Click Apply — router will reboot into the new mode

**After switching to AP or WDS mode:**
- Access `192.168.8.1` will stop working
- Find the router's new IP in the upstream router's DHCP client table
- To recover without knowing the IP: hold the reset button until touchscreen shows "Release to Repair Mode"

### Configure Port Forwarding

1. Admin Panel → Network → Firewall (or Network → Port Forwarding)
2. Click **Add Rule**
3. Enter:
   - Name (descriptive label)
   - Protocol (TCP, UDP, or both)
   - External port (the port exposed to the internet)
   - Internal IP (LAN device receiving the traffic)
   - Internal port (the port on the LAN device)
4. Click Apply
5. Verify with an external port checker tool once a WAN connection is active

### Update Firmware (Online)

1. Admin Panel → System → Upgrade
2. Click **"Check for Updates"**
3. If an update is available, click to download and install
4. Router reboots automatically (~2–3 minutes); do not power off during flashing

### Update Firmware (Manual / Local)

1. Download the correct `.bin` firmware file for GL-BE3600 from `https://dl.gl-inet.com/router/be3600/`
2. Admin Panel → System → Upgrade → **Local Upgrade** tab
3. Click "Choose File" → select the `.bin` file
4. Click Upload / Update
5. Router flashes and reboots automatically
6. Only flash firmware explicitly built for GL-BE3600; flashing a wrong model's file will brick the device

### Change Admin Password

Admin Panel → System → Security → Change Admin Password → enter current password, new password, confirm → Apply
