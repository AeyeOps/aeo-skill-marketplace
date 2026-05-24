# Installing Tailscale on macOS

Covers the install path that works reliably with a headscale coordinator on
macOS Tahoe and later: Homebrew Cask, the NetworkExtension permission grants,
how to detect and clean up a conflict with the brew formula, and how to
confirm the daemon is reachable before attempting to join.

---

## Distribution choice

Two distinct Tailscale packages exist on macOS, both named `tailscale`:

| Package | Install command | What it provides | Use for headscale? |
|---------|-----------------|------------------|--------------------|
| **Homebrew Cask** | `brew install --cask tailscale` | The full `Tailscale.app` GUI, the NetworkExtension daemon (`IPNExtension`), a menu-bar UI, an auto-start LaunchAgent, and a single binary that doubles as both GUI and CLI. | **Yes — recommended.** |
| Homebrew formula | `brew install tailscale` | Standalone `tailscaled` daemon and `tailscale` CLI, separate from any `.app` bundle. Modeled after the Linux client. | Possible but discouraged on macOS; loses the macOS-integrated VPN experience and conflicts with the cask if both are installed. |
| Mac App Store | (App Store GUI) | App-sandboxed build of the same `Tailscale.app`. | Avoid mixing with the cask — they install to the same path and override each other unpredictably. |

The procedures in this skill assume the cask. Use one distribution at a time.

---

## Fresh install

```sh
brew install --cask tailscale
open -a Tailscale
```

On first launch the OS will display a sequence of permission prompts to
allow the bundled NetworkExtension to load and to install a VPN
configuration. These must all be granted before the daemon will start.

### Permission dance (macOS Tahoe pane locations)

Tahoe-era macOS scatters the relevant toggles across several panes. Walk all
four if the daemon is not appearing in `pgrep -fl IPNExtension` after
launching the app:

1. **System Settings → Privacy & Security → Security** (scroll near the
   bottom). Look for a recently-shown "Allow" button next to a Tailscale
   message. Click it.
2. **System Settings → General → Login Items & Extensions → Network
   Extensions**. Toggle Tailscale **on**.
3. **System Settings → Network → VPN** (sidebar). A "Tailscale" VPN
   configuration should appear; ensure its toggle is on.
4. **System Settings → Privacy & Security → Local Network** (if prompted).
   Allow Tailscale.

After granting these, fully quit Tailscale.app (menu-bar icon → Quit) and
reopen it: `open -a Tailscale`. Within a few seconds, the daemon should
register:

```sh
pgrep -fl IPNExtension
# expect: an /Applications/Tailscale.app/Contents/PlugIns/IPNExtension.appex path
```

---

## "failed to connect to local tailscale service"

That error from the CLI means the binary started fine but cannot reach the
daemon's IPC channel. On macOS the daemon is the NetworkExtension; if it has
not been activated, there is nothing for the CLI to talk to. The fix is
always one of:

| Cause | How to confirm | Fix |
|-------|----------------|-----|
| Tailscale.app is not open | `pgrep -fl 'Tailscale.app/Contents/MacOS/Tailscale'` returns nothing | `open -a Tailscale` |
| NetworkExtension not activated | `systemextensionsctl list` shows Tailscale in `waiting for user` or absent | Walk the "Permission dance" above |
| Mixed cask + formula install | `pgrep -fl tailscaled` returns a non-app binary path (`/opt/homebrew/...` or `/usr/local/...`) | Cleanup procedure below |
| App is running but the daemon process crashed | `pgrep -fl IPNExtension` returns nothing despite the GUI being open | Quit and reopen Tailscale.app; check `log show --predicate 'subsystem == "io.tailscale.ipn"' --last 5m` |

---

## Cleaning up a mixed cask + formula install

Symptom: Tailscale.app GUI gets stuck on "Starting...", `tailscale up` hangs
without output, or `tailscale status` returns "failed to connect to local
tailscale service" even though the GUI is open. Run as root:

```sh
# 1. Stop the formula daemon (as user and as root — coverage for both modes)
brew services stop tailscale 2>/dev/null || true
sudo brew services stop tailscale 2>/dev/null || true
sudo launchctl bootout system /Library/LaunchDaemons/homebrew.mxcl.tailscale.plist 2>/dev/null || true
sudo launchctl bootout system /Library/LaunchDaemons/com.tailscale.tailscaled.plist 2>/dev/null || true

# 2. Quit the cask app cleanly so it releases its socket
osascript -e 'tell application "Tailscale" to quit' 2>/dev/null || true
sleep 2

# 3. Kill any straggler tailscaled
sudo pkill -x tailscaled 2>/dev/null || true

# 4. Remove the brew formula entirely (keeps Tailscale.app)
brew uninstall tailscale 2>/dev/null || true

# 5. Reopen the cask app cleanly
open -a Tailscale
```

After step 5, allow ~10s and re-check with `pgrep -fl IPNExtension`. If the
extension does not return, the permission dance still has steps left — see
the table above.

---

## Verifying the install is healthy

These four checks together confirm a clean baseline before attempting to
join a mesh:

```sh
# A. Cask app installed
ls -d /Applications/Tailscale.app

# B. No formula daemon competing
pgrep -fl tailscaled | grep -v 'Tailscale.app' && echo "PROBLEM" || echo "ok"

# C. Daemon process running
pgrep -fl IPNExtension >/dev/null && echo "ok" || echo "daemon not running"

# D. CLI can reach daemon
/Applications/Tailscale.app/Contents/MacOS/Tailscale status >/dev/null 2>&1 \
  && echo "ok" || echo "CLI cannot reach daemon"
```

Once all four return success, proceed to
[joining-headscale-from-macos.md](joining-headscale-from-macos.md).
