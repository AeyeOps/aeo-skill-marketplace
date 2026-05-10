# GL-iNet Slate 7 — Initial Setup and Interactive Management

## Table of Contents
- [Initial Physical Connection](#initial-physical-connection)
- [First-Time Setup Wizard](#first-time-setup-wizard)
- [Direct Connection (No Internet Upstream)](#direct-connection-no-internet-upstream)
- [SSH and CLI Access](#ssh-and-cli-access)
- [Troubleshooting Connection Issues](#troubleshooting-connection-issues)
- [Firmware Updates](#firmware-updates)
- [U-Boot Recovery (Bricked Device)](#u-boot-recovery-bricked-device)

---

## Initial Physical Connection

### Hardware Preparation
1. Unfold both external antennas for optimal signal
2. Connect USB-C power (5V/3A minimum; 9V/3A or 12V/2.5A preferred for stability)
3. Wait ~30 seconds for the touchscreen to activate and Wi-Fi to begin broadcasting

### Connecting Your Computer to the Router

**Via Ethernet (most reliable, recommended for initial setup):**
Connect an Ethernet cable from your computer's LAN port to the router's **LAN** port (not WAN). Your computer receives an IP in the `192.168.8.0/24` range via DHCP automatically.

**Via Wi-Fi:**
- Look at the bottom label of the router for the SSID and default password
- SSID format: `GL-BE3600-XXX` (2.4 GHz) or `GL-BE3600-XXX-5G` (5 GHz), where XXX is a device-specific suffix
- Default Wi-Fi password: printed on the label; fallback common default is `goodlife` if label is unreadable
- A QR code on the label encodes these credentials — scan with a smartphone camera to connect quickly

### Reaching the Admin Panel
Open a browser and navigate to:
```
http://192.168.8.1
```
Use HTTP, not HTTPS. Chrome, Edge, or Safari recommended. The first-time setup wizard loads automatically.

---

## First-Time Setup Wizard

The wizard runs on the first browser visit to `http://192.168.8.1`.

### Step 1: Language Selection
Choose your preferred interface language from the dropdown. Click **Next**.

### Step 2: Set Admin Password
Create a strong admin password (minimum 5 characters).

This password is used for:
- Web admin panel login
- SSH root login via CLI

**There is no factory-default admin password.** You must create one. The router will not be fully functional until this step is complete.

Click **Apply** or **Submit**. The router may briefly disconnect Wi-Fi during initialization — reconnect to the same SSID, then return to `http://192.168.8.1`.

### Step 3: Internet Source Selection
The dashboard presents four connection options:

| Option | When to Use |
|--------|-------------|
| **Ethernet** | WAN port connected to modem or upstream router |
| **Repeater** | Connect to existing Wi-Fi as upstream (WISP mode) |
| **Tethering** | USB-tethered smartphone or Bluetooth |
| **Cellular** | USB 4G/5G modem plugged into USB 3.0 port |

Click the appropriate tile and complete its sub-steps (e.g., selecting and authenticating to an upstream Wi-Fi for Repeater mode).

### Alternative: GL.iNet Mobile App Setup
Download the GL.iNet app (iOS or Android), scan the QR code on the router's label, and follow in-app prompts as an alternative to browser-based setup.

---

## Direct Connection (No Internet Upstream)

The router's admin panel and LAN services remain fully functional even without a WAN/internet connection.

### Wired Direct Connection
Connect an Ethernet cable between your computer and the router's **LAN** port. Your computer will receive a DHCP address in the `192.168.8.0/24` subnet. Admin panel at `http://192.168.8.1` is always reachable this way.

### Wi-Fi Direct Connection
The router broadcasts its SSIDs even when no upstream internet exists. Connect to `GL-BE3600-XXX` using label credentials. The router provides DNS and DHCP to connected clients; those clients will have local LAN access but no internet connectivity until a WAN is configured.

### Admin Panel in Different Network Modes

| Mode | Admin Panel After Switch | Recovery if Lost |
|------|--------------------------|-----------------|
| **Router** (default) | `192.168.8.1` — always | N/A |
| **Access Point** | New DHCP-assigned IP — check upstream router's client table | Hold reset → "Release to Repair Mode" |
| **Extender** | `192.168.8.1` — still works | N/A |
| **WDS** | New DHCP-assigned IP — check upstream router's client table | Hold reset → "Release to Repair Mode" |
| **Drop-in Gateway** | Accessible at Slate 7's own IP | N/A |

---

## SSH and CLI Access

### SSH is Enabled by Default
No additional configuration is required to activate SSH access.

### Credentials
| Field | Value |
|-------|-------|
| Username | `root` |
| Password | Same as admin panel password (set during first-time setup) |
| Default IP | `192.168.8.1` |
| Port | `22` |

### Connecting via SSH

**macOS / Linux / Windows Terminal / PowerShell:**
```bash
ssh root@192.168.8.1
# Type "yes" if prompted about host authenticity (first connection)
# Enter admin password when prompted (input will not be echoed to screen)
```

**Windows — PuTTY:**
- Host Name: `192.168.8.1`
- Port: `22`
- Connection Type: SSH
- Login as: `root`

**Non-default port:**
```bash
ssh -p <port_number> root@192.168.8.1
```

### Host Key Warning After Factory Reset
After a factory reset the router generates a new SSH host key. Clear the cached old key:
```bash
ssh-keygen -f ~/.ssh/known_hosts -R "192.168.8.1"
```
Then reconnect normally.

### Useful CLI Commands

The router runs OpenWrt. All standard OpenWrt commands apply.

**System information:**
```bash
uname -a                         # Kernel and OS details
cat /etc/openwrt_release         # GL firmware version and OpenWrt release
uptime                           # System uptime and load
free -m                          # Memory usage in MB
df -h                            # Disk/flash usage
```

**Network status:**
```bash
ifconfig                         # Interface status and IPs
ip route                         # Routing table
ip addr                          # All interface addresses
cat /etc/config/network          # UCI network configuration file
```

**Package management (opkg):**
```bash
opkg update                      # Refresh package list from repository
opkg list-installed              # List all installed packages
opkg install <package-name>      # Install a package
opkg remove <package-name>       # Remove a package
opkg list | grep <keyword>       # Search available packages
```

**Service control:**
```bash
/etc/init.d/<service> status     # Check a service's running state
/etc/init.d/<service> start      # Start a service
/etc/init.d/<service> stop       # Stop a service
/etc/init.d/<service> restart    # Restart a service
/etc/init.d/<service> enable     # Enable service at boot
/etc/init.d/<service> disable    # Disable service at boot
```

**Common service names:** `network`, `firewall`, `dnsmasq`, `uhttpd` (web UI), `wireguard`, `openvpn`, `adguardhome`

**Configuration (UCI):**
```bash
uci show                         # Show all UCI configuration
uci show network                 # Show network configuration only
uci get network.lan.ipaddr       # Get a specific value
uci set network.lan.ipaddr='192.168.8.1'  # Set a value
uci commit                       # Persist changes to disk
/etc/init.d/network reload       # Apply network changes without reboot
```

**Firewall:**
```bash
fw4 reload                       # Reload nftables firewall rules (newer firmware)
fw4 list                         # List current firewall rules
```

**Logs:**
```bash
logread                          # Show system log (recent entries)
logread -f                       # Follow system log live (Ctrl+C to stop)
logread -e "wireguard"           # Filter log for specific keyword
dmesg                            # Kernel message buffer
```

**Processes and diagnostics:**
```bash
top                              # Real-time process view (q to quit)
ps                               # Running processes
ping 1.1.1.1                     # Test connectivity
traceroute 1.1.1.1               # Trace network path
nslookup google.com              # DNS lookup test
```

**Reboot:**
```bash
reboot
```

### Changing LAN IP via CLI
If you need to change the router's LAN IP (e.g., to avoid subnet conflicts):
```bash
uci set network.lan.ipaddr='192.168.10.1'
uci commit network
/etc/init.d/network restart
```
After the restart, reconnect and use the new IP to access the admin panel.

---

## Troubleshooting Connection Issues

### Cannot Reach `http://192.168.8.1`

| Cause | Fix |
|-------|-----|
| Connected to wrong network | Confirm your device is on the router's SSID or LAN |
| Router in AP or WDS mode | The IP changed; find new IP from upstream router, or do soft reset |
| Browser using HTTPS | Navigate to `http://` (not `https://`) explicitly |
| Cached redirect in browser | Try incognito/private browser window |
| Router still booting | Wait 30–60 seconds after power-on and retry |

### Forgot Admin Password
Factory reset is required — the password cannot be recovered without resetting:
1. Hold the reset button until the touchscreen shows **"Release to Reset Mode"**
2. Release — the router erases all data and reboots
3. Run the first-time setup wizard again

### Reset Button Behavior (Touchscreen-Guided)

The Slate 7 uses a touchscreen-guided reset flow instead of fixed hold durations.

**Soft Reset (Repair Mode):**
1. Fully boot the router first (touchscreen must be active)
2. Hold the reset button
3. When touchscreen shows **"Release to Repair Mode"** → release immediately
4. Effect: reboots network interfaces, restores WAN/network defaults
5. Preserved: Wi-Fi SSID/password, VPN configurations, admin password, installed plugins
6. Also re-enables Wi-Fi if it was manually turned off

**Factory Reset (Reset Mode):**
1. Continue holding past the Repair Mode prompt
2. When touchscreen shows **"Release to Reset Mode"** → release
3. Effect: erases all configurations, returns to factory state
4. The touchscreen shows GL.iNet branding on restart
5. All settings are gone — run first-time setup wizard on next browser access

**Do not press reset immediately after powering on.** The router must fully boot before reset button presses are processed. Pressing during early boot may accidentally enter U-Boot failsafe mode.

### Factory Reset via Admin Panel
Admin Panel → System → Reset Firmware → click **"Delete All and Reboot"**
- Takes approximately 2 minutes
- Do not power off during the process
- Router reboots to factory state automatically

### Admin Panel Unreachable After Mode Change
If you switched to AP or WDS mode and can no longer reach `192.168.8.1`:

**Option A — Find new IP:**
Log into your upstream router's admin panel → look at the DHCP client table → find the GL-BE3600 entry → use that IP in your browser.

**Option B — Soft reset to Router Mode:**
Hold reset button until touchscreen shows "Release to Repair Mode" → release. The router reverts to Router Mode with `192.168.8.1` accessible again.

### Wi-Fi Not Broadcasting
- Soft reset (Repair Mode) re-enables Wi-Fi if it was disabled
- Check Admin Panel → Wireless — confirm both bands are toggled on
- Via CLI: `/etc/init.d/network restart`

---

## Firmware Updates

### Check Current Firmware Version
Admin Panel → System → Overview → Device Info section shows:
- Current firmware version
- OpenWrt version
- Kernel version
- Device ID, MAC address, serial number

### Online (OTA) Update
1. Admin Panel → System → Upgrade
2. Click **"Check for Updates"**
3. If a new version is available: click to download and install
4. Router reboots after flashing (~2–3 minutes)
5. Do not power off during the process

### Local (Manual) Update
1. Download the correct firmware `.bin` for GL-BE3600 from `https://dl.gl-inet.com/router/be3600/`
2. Admin Panel → System → Upgrade → **Local Upgrade** tab
3. Click "Choose File" → select the `.bin` file
4. Click Upload / Update
5. Router flashes and reboots automatically

**Critical:** Only flash firmware files explicitly labeled for the GL-BE3600. Flashing a file for a different model will brick the device.

### After Update
- Admin panel may briefly show cached content — open an incognito/private window and navigate to `http://192.168.8.1`
- Most settings are preserved across firmware updates unless you explicitly choose to reset during the update
- Review release notes for any changed defaults or removed features

---

## U-Boot Recovery (Bricked Device)

Use this when the router cannot boot normally — stuck in a boot loop, admin panel unreachable after a failed firmware flash, or firmware is corrupted.

### When to Use U-Boot Recovery
- Router stuck in a boot loop (reboots repeatedly)
- Admin panel unreachable after a bad firmware flash
- Standard factory reset does not help
- Device makes no progress past the GL.iNet splash on the touchscreen

### Entering U-Boot Mode

1. **Power off** the router completely (disconnect USB-C)
2. **Press and hold** the reset button firmly
3. **While still holding**, reconnect USB-C power
4. Continue holding — after approximately 5 seconds, a **countdown** appears on the touchscreen
5. Continue holding through the countdown until additional prompts appear
6. The touchscreen will display instructions — follow them; it will prompt you to set your computer's IP manually

### Configure Your Computer's Ethernet Adapter

Set your computer's wired Ethernet connection to static:
- **IP Address:** `192.168.1.2`
- **Subnet Mask:** `255.255.255.0`
- **Gateway:** `192.168.1.1` (or leave blank)
- **DNS:** leave blank

Connect your computer to the router's **LAN** port with an Ethernet cable.

### Access the U-Boot Web Interface

Open a browser and navigate to:
```
http://192.168.1.1
```
A plain HTML recovery interface loads (very basic, no styling — this is normal).

### Flash Firmware via U-Boot

1. Download U-Boot-compatible firmware for GL-BE3600 from `https://dl.gl-inet.com/router/be3600/`
   - Look for a file marked for factory/U-Boot flashing; it may differ from the OTA upgrade file
2. In the U-Boot web UI: click **"Choose File"** → select the firmware file
3. Click **"Update Firmware"**
4. Wait approximately 3 minutes — the page will appear to hang; this is normal during flash
5. **Do NOT power off the device during this period**
6. The router reboots automatically when flashing completes

### After U-Boot Recovery

1. Revert your computer's network adapter back to **DHCP (automatic)**
2. Wait ~30 seconds for the router to complete its first boot
3. Connect to the router via Ethernet (LAN port) or Wi-Fi (`GL-BE3600-XXX`)
4. Open a browser in incognito/private mode → navigate to `http://192.168.8.1`
5. All settings were erased — run the first-time setup wizard
6. If the page doesn't load, wait another 30 seconds and refresh

### Quick Reference Summary

| Situation | Action |
|-----------|--------|
| Admin panel unreachable (mode change) | Find new IP from upstream DHCP, or soft reset |
| Forgot admin password | Factory reset via reset button or Admin Panel |
| Wi-Fi not broadcasting | Soft reset (Repair Mode) or check Wireless settings |
| Intermittent Repeater drops | Known firmware issue; retry connection; check for firmware updates |
| Router stuck booting | Enter U-Boot recovery mode |
| Wrong firmware flashed | Enter U-Boot recovery mode; flash correct GL-BE3600 firmware |
| SSH "host key changed" error | Run `ssh-keygen -f ~/.ssh/known_hosts -R "192.168.8.1"` |
