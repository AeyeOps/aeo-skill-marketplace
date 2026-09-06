#!/usr/bin/env python3
"""Enumerate Claude Cowork projects (spaces) and sessions, on Windows or macOS.

Reads the Cowork profile straight off disk and reports the project list and
per-session stats. It exists because answering "what projects/sessions do I have"
by hand takes several stumbles: the project count must come from spaces.json (the
spaces/ subdir is lazily created and undercounts), sidecars carry two different
session IDs, and the transcript lives under a per-machine encoded-cwd directory.

Design choices:
- Stdlib only, so it runs on a fresh macOS box without `uv`/pip setup.
- No hardcoded account/profile UUIDs or user home: everything is discovered by
  enumeration, so the same script works on any machine and on a copied profile
  (pass --base to point at an extracted bundle).
- spaces.json is the authoritative project registry. See storage-layout.md.

Usage:
    python session-enum.py                 # human-readable report for this machine
    python session-enum.py --json          # machine-readable JSON
    python session-enum.py --base <dir>    # point at a specific Claude support dir
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
SIDECAR_RE = re.compile(r"^local_[0-9a-fA-F-]{36}\.json$")
SESSIONS_ROOT_NAMES = ("local-agent-mode-sessions", "claude-code-sessions")


def default_base() -> Path:
    """The Claude support directory for the current OS."""
    if sys.platform == "win32":
        import os

        appdata = os.environ.get("APPDATA")
        if not appdata:
            sys.exit("APPDATA is not set; pass --base explicitly.")
        return Path(appdata) / "Claude"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Claude"
    sys.exit(f"Unsupported platform {sys.platform!r}; pass --base explicitly.")


def find_profiles(base: Path) -> list[Path]:
    """Every <account>/<profile> directory under the sessions root."""
    root = next((base / n for n in SESSIONS_ROOT_NAMES if (base / n).is_dir()), None)
    if root is None:
        sys.exit(
            f"No sessions root under {base} "
            f"(looked for {', '.join(SESSIONS_ROOT_NAMES)})."
        )
    profiles: list[Path] = []
    for account in sorted(p for p in root.iterdir() if p.is_dir() and UUID_RE.match(p.name)):
        profiles.extend(sorted(p for p in account.iterdir() if p.is_dir() and UUID_RE.match(p.name)))
    return profiles


def load_spaces(profile: Path) -> list[dict]:
    spaces_json = profile / "spaces.json"
    if not spaces_json.is_file():
        return []
    data = json.loads(spaces_json.read_text(encoding="utf-8"))
    return data.get("spaces", [])


def iter_sidecars(profile: Path):
    """Yield (session_id, sidecar_data) for each real sidecar, skipping .bak/.orig."""
    for path in sorted(profile.glob("local_*.json")):
        if not SIDECAR_RE.match(path.name):
            continue
        yield path.stem, json.loads(path.read_text(encoding="utf-8"))


def find_transcript(profile: Path, session_id: str, cli_session_id: str) -> Path | None:
    projects = profile / session_id / ".claude" / "projects"
    if not projects.is_dir():
        return None
    return next(projects.glob(f"*/{cli_session_id}.jsonl"), None)


def transcript_stats(path: Path) -> dict:
    by_type: dict[str, int] = {}
    lines = compact_boundaries = parse_errors = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            lines += 1
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                parse_errors += 1
                continue
            by_type[ev.get("type", "?")] = by_type.get(ev.get("type", "?"), 0) + 1
            if ev.get("subtype") == "compact_boundary":
                compact_boundaries += 1
    return {
        "bytes": path.stat().st_size,
        "lines": lines,
        "messages": by_type.get("user", 0) + by_type.get("assistant", 0),
        "by_type": by_type,
        "compact_boundaries": compact_boundaries,
        "parse_errors": parse_errors,
    }


def build_report(profile: Path) -> dict:
    spaces = load_spaces(profile)
    by_id = {s["id"]: s for s in spaces}
    projects = {
        s["id"]: {
            "name": s.get("name", "(unnamed)"),
            "folders": [f.get("path") for f in s.get("folders", [])],
            "linkedProjectUuid": (s.get("projects") or [{}])[0].get("uuid"),
            "sessions": [],
        }
        for s in spaces
    }
    orphans: list[dict] = []
    sidecars = list(iter_sidecars(profile))

    for session_id, side in sidecars:
        cli = side.get("cliSessionId")
        transcript = find_transcript(profile, session_id, cli) if cli else None
        entry = {
            "sessionId": session_id,
            "cliSessionId": cli,
            "title": side.get("title") or side.get("name") or "(untitled)",
            "vmProcessName": side.get("vmProcessName"),
            "userSelectedFolders": side.get("userSelectedFolders", []),
            "fsDetectedFiles": len(side.get("fsDetectedFiles", [])),
            "hasTranscript": transcript is not None,
            "stats": transcript_stats(transcript) if transcript else None,
        }
        space_id = side.get("spaceId")
        if space_id and space_id in projects:
            projects[space_id]["sessions"].append(entry)
        else:
            orphans.append(entry)

    return {
        "profile": f"{profile.parent.name}/{profile.name}",
        "projectCount": len(spaces),
        "sessionCount": sum(len(p["sessions"]) for p in projects.values()) + len(orphans),
        "projects": list(projects.values()),
        "orphanSessions": orphans,
        "unknownSpaceIds": sorted(
            {
                side.get("spaceId")
                for _, side in sidecars
                if side.get("spaceId") and side.get("spaceId") not in by_id
            }
        ),
    }


def fmt_bytes(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"


def print_human(report: dict) -> None:
    print(f"Profile {report['profile']}: "
          f"{report['projectCount']} projects, {report['sessionCount']} sessions\n")
    for p in report["projects"]:
        link = f"  [synced project {p['linkedProjectUuid']}]" if p["linkedProjectUuid"] else ""
        print(f"# {p['name']}  ({len(p['sessions'])} sessions){link}")
        for folder in p["folders"]:
            print(f"    folder: {folder}")
        for s in sorted(p["sessions"], key=lambda e: -(e['stats']['messages'] if e['stats'] else 0)):
            _print_session(s)
        print()
    if report["orphanSessions"]:
        print(f"# (orphan sessions, no project)  ({len(report['orphanSessions'])} sessions)")
        for s in sorted(report["orphanSessions"], key=lambda e: -(e['stats']['messages'] if e['stats'] else 0)):
            _print_session(s)
        print()
    if report["unknownSpaceIds"]:
        print("WARNING: sidecars reference spaceIds not in spaces.json: "
              + ", ".join(report["unknownSpaceIds"]))


def _print_session(s: dict) -> None:
    if s["stats"]:
        st = s["stats"]
        meta = (f"{st['messages']} msgs, {fmt_bytes(st['bytes'])}, "
                f"{st['compact_boundaries']} compactions")
        if st["parse_errors"]:
            meta += f", {st['parse_errors']} parse-errors"
    else:
        meta = "no transcript found"
    vm = f", vm={s['vmProcessName']}" if s["vmProcessName"] else ""
    print(f"    - {s['title'][:60]!r}  ({meta}{vm})")


def main() -> None:
    ap = argparse.ArgumentParser(description="Enumerate Cowork projects and sessions.")
    ap.add_argument("--base", type=Path, help="Claude support dir (default: per-OS).")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of a report.")
    args = ap.parse_args()

    base = args.base or default_base()
    reports = [build_report(profile) for profile in find_profiles(base)]

    if args.json:
        print(json.dumps(reports if len(reports) != 1 else reports[0], indent=2))
        return
    for report in reports:
        print_human(report)


if __name__ == "__main__":
    main()
