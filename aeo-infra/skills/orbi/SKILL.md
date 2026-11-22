---
name: orbi
description: |
  Use when diagnosing NETGEAR Orbi mesh Wi-Fi through its local admin UI, activity log,
  and client radio observations. Covers RBE970-series log access, satellite identification,
  stale repeater BSSID locks, and verifying the uplink on a dual-homed client.
license: MIT
metadata:
  author: AeyeOps
  version: "0.7.0"
  summary: Diagnose Orbi mesh and repeater failures and verify the end-to-end uplink.
---

# Orbi diagnostics

## Reach the correct router

On a computer connected to both an Orbi and a repeater, identify the local addresses and routes to both gateways. On Windows use `Find-NetRoute -RemoteIPAddress <gateway>`. The default internet route or currently connected Wi-Fi name alone can point at the wrong device. Open the Orbi's LAN HTTPS address and confirm the NETGEAR Orbi login page. Use its local admin account. Keep the repeater's credentials with the repeater.

## Read the activity log

Open **Advanced → Administration → Logs**. Record the oldest and newest parseable timestamps, the router's time zone if known, and any unparseable entries before assessing an incident. Count the actual records. The RBE971/RBE970 manual describes a 256-entry limit, but an observed RBE971 Logs page returned 400 dated entries. An admin login establishes access at that time. A change to an SSID, BSSID, or security mode needs evidence identifying that change. [NETGEAR manual, pp. 102–104](https://assets.netgear.com/asset/9c0111dc-9bf7-4b45-8ea9-668865f05e9b/RBE971_RBE970_UM.pdf#page=102)

For the Orbi 970 local web UI with AJAX login, run `scripts/read_logs.py` with Python 3.10 or newer. The helper checks the login form before requesting a password, uses the menu's Logs page, and emits a summary. Use `--source` to bind the router-facing adapter on a dual-homed machine. Read detailed login and validation steps in [Local admin access](references/local-admin.md).

For previously copied log text or saved Logs HTML, run `python scripts/summarize_log.py log.txt --date YYYY-MM-DD`. Keep original logs local. Retain counts, relevant event times, and the coverage limits in the diagnosis.

## Trace a repeater association failure

1. Read the repeater's saved upstream profile and failure reason. Record the exact SSID, any pinned BSSID, and any band restriction. Record when and where the repeater's survey was collected. Distinguish a cached survey from a fresh observation.
2. Compare the full BSSID against the BSSIDs actually advertising the saved SSID on the requested band. SSIDs can be shared across mesh nodes. A unit's base MAC, client MAC, and per-SSID radio BSSID serve different purposes. Matching trailing octets alone does not identify an access point.
3. For a pinned profile, run `python scripts/compare_bssid.py survey.csv --ssid "Example WiFi" --bssid 02:00:00:00:00:01 --band 5GHz`. The CSV header is `ssid,bssid,band,channel`. Omit `--band` for an unrestricted profile. For an SSID-only profile, list all candidates on the allowed bands and check which BSSID the repeater attempted. A missing target plus a repeater reporting no matching BSS places that attempt before authentication and DHCP. A second survey can corroborate visibility if location, band and time are comparable.
4. For visible targets, use the actual association and authentication result. For a completed association, inspect lease assignment and reachability. Use the Orbi's current Wireless Settings to corroborate band, configured channel, and security mode. Treat current settings and observed changes over time as distinct evidence.

During diagnosis, use the existing status, log, and survey data. A forced reconnect, settings submission, or log clear changes the conditions under investigation.

A BSSID lock can be deliberate when a stationary repeater repeatedly selects a poorly performing mesh node. Before recommending a replacement pin, identify which node advertises the candidate BSSID and compare end-to-end performance from the repeater. Signal strength alone cannot establish the quality of a satellite's path to the router. A saved pin alone does not establish why it was chosen.

For a Slate 7 that must stay on 5 GHz, retain the **5 GHz** band selection. Clearing **Lock BSSID** lets the Slate choose among eligible Orbi radios on that band. See [Clear and verify a Slate repeater pin](references/slate-repeater.md) for the browser and API procedures, the saved-field comparison, and an interface-bound HTTPS test.

## Maintain this skill

When the operator requests ongoing skill maintenance, retain verified procedures, parser corrections, firmware differences, and reusable checks. Test changed helpers with a synthetic case and record any limits of live validation. Keep incident timelines, household identifiers, passwords, and session state out of the skill.
