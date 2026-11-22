# Clear and verify a Slate repeater pin

Use this procedure when the Slate reports no matching access point, its saved profile specifies a BSSID absent from a survey, and another radio advertises the same SSID on the allowed band. Record whether the survey was cached. A lock-only change belongs on the Slate. The Orbi can remain online throughout.

## Browser

On the Slate, open **Internet → Repeater → Connect** (or **Switch Network**), then the gear beside the SSID under **Known Networks**. Clear **Lock BSSID** and reconnect. On the join form the lock appears under **Advanced Settings**. **Repeater Options → Band Selection** controls the allowed band independently. A profile already limited to 5 GHz needs no band edit. [GL.iNet repeater guide](https://docs.gl-inet.com/router/en/4/interface_guide/internet_repeater/#advanced-settings)

## Local JSON-RPC

Use the Slate's local HTTPS admin session. On the tested GL-BE3600 interface, the browser authenticates with the local admin password through `challenge` and `login` for the RPC account `root`. Follow the account and challenge algorithm advertised by the device's own login UI. Each authenticated module call uses `[sid, "repeater", method, parameters]`. Saved profiles can include the Wi-Fi key. Keep credentials, session IDs, and complete responses in memory.

1. Read `get_config`, `get_saved_ap_list` (entries are in `res`), and `get_status`. Find exactly one saved entry matching the target SSID. Check that its `bssid` is the expected stale pin and that `get_config.lock_band` already meets the requested policy (`5g` for 5 GHz). If the pin is absent, go directly to verification.
2. Before submitting an authorized change, re-read the saved entries and global config. If another admin edited them, inspect the newer values first. Copy the target entry, remove only `bssid`, and set the form's submit flag `remember` to `true`. Preserve its key, MAC settings, and every other connection option. If the key is masked or required settings cannot be preserved, use the saved network's browser editor.
3. Submit that copy **once** to `repeater.connect`. On this firmware, the browser omits `bssid` when the lock is off. The checkbox name `lock_bssid` is local to the form. The global `set_config` call and deleting/recreating the profile are unnecessary. If the response is interrupted, read back the saved profile before considering another write.

## Verify the saved settings, association, and client path

- **Saved settings.** Re-read the saved entries. Compare the target against the original with just its BSSID removed (an empty pin can also represent unlocked). Compare the other saved entries and the global repeater config with their originals. Report field names if anything else differs. Keep the credential values private.
- **Association.** Poll `repeater.get_status` through reconnection. On the verified firmware, `state=2` accompanied a connected link. Confirm the live SSID, band, channel, active BSSID, and IPv4 gateway or lease. The connected radio has a BSSID even when the saved profile has no pin.
- **Client path.** On a dual-homed Windows or Linux client, identify the interface facing the Slate and its local IPv4 address. On Windows, use `Get-NetIPConfiguration` and match the interface's gateway to the Slate; on Linux use `ip -4 route`, `ip -4 addr` and `ip link`. From the skill directory, run the command below. It checks HTTPS to Cloudflare using the named adapter's index and source address. Use `--address` and `--hostname` for another HTTPS endpoint. The numeric destination isolates the HTTPS test from DNS. For a tailnet SSH test, run a remote command such as `tssh <node> hostname`. That verifies tailnet access; use the interface-bound check to attribute internet access to the repeater.

```text
python scripts/verify_uplink.py --interface-index <index> --source <client-ipv4>
```
