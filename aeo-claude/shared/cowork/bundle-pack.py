#!/usr/bin/env python3
"""Pack one Cowork project (space) into a portable .coworkbundle directory.

Export is a pure copy plus a manifest: it never rewrites paths. Every absolute
source path is left byte-for-byte intact and the anchors needed to retarget them
(source OS, user, home, base, per-session cwd/encodedCwd) are recorded in
manifest.json, so a single bundle can later be imported onto Windows OR macOS.
bundle-unpack.py does the rewriting on the destination.

What travels, per session: the sidecar, the transcript JSONL and its nested
subagents/ + tool-results/ tree, outputs/, uploads/, and the audit log. What is
deliberately left out: .credentials.json and mcp-needs-auth-cache.json (machine
and account bound; the destination re-auths), .claude/backups/, and the
shim-lib/shim-perm runtime dirs. VM-only files (sessiondata.vhdx) are not mounted
here; pass --vm-files <dir> with a pre-extracted tree (see vhdx-extract.md) to
include them, otherwise sessions that reference VM paths are flagged in warnings.

Stdlib only, so it runs on a fresh macOS box as well as Windows. See
storage-layout.md for the structures and bundle-manifest.schema.json for the
manifest contract.

Usage:
    python bundle-pack.py "Example Project"          # by project name
    python bundle-pack.py 45152ea1-...               # by spaceId
    python bundle-pack.py "Example Project" --out ~/cowork-bundles --force
    python bundle-pack.py "Example Project" --vm-files ~/extracted-vm
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
SIDECAR_RE = re.compile(r"^local_[0-9a-fA-F-]{36}\.json$")
SESSIONS_ROOT_NAMES = ("local-agent-mode-sessions", "claude-code-sessions")


# --- discovery (mirrors session-enum.py; small and stable, kept local on purpose) ---

def default_base() -> Path:
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
    root = next((base / n for n in SESSIONS_ROOT_NAMES if (base / n).is_dir()), None)
    if root is None:
        sys.exit(f"No sessions root under {base}.")
    profiles: list[Path] = []
    for account in sorted(p for p in root.iterdir() if p.is_dir() and UUID_RE.match(p.name)):
        profiles.extend(sorted(p for p in account.iterdir() if p.is_dir() and UUID_RE.match(p.name)))
    return profiles


def load_spaces(profile: Path) -> list[dict]:
    sj = profile / "spaces.json"
    return json.loads(sj.read_text(encoding="utf-8")).get("spaces", []) if sj.is_file() else []


# --- helpers ---

def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return s or "project"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_transcript(path: Path, vm: str | None) -> tuple[int, int, bool]:
    compactions = 0
    vm_ref = False
    needle = f"/sessions/{vm}/" if vm else None
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"compact_boundary"' in line:
                compactions += 1
            if needle and not vm_ref and needle in line:
                vm_ref = True
    return path.stat().st_size, compactions, vm_ref


def classify(rel: str) -> str:
    name = rel.rsplit("/", 1)[-1]
    if rel == "space/spaces-entry.json":
        return "space-entry"
    if rel.startswith("space/memory/"):
        return "space-memory"
    if "/vm-files/" in rel:
        return "vm-file"
    if name == "sidecar.json":
        return "sidecar"
    if "/outputs/" in rel:
        return "output"
    if "/uploads/" in rel:
        return "upload"
    if "/transcript/" in rel:
        if "/subagents/" in rel:
            return "subagent-meta" if name.endswith(".meta.json") else "subagent"
        if "/tool-results/" in rel:
            return "tool-result"
        if name.endswith(".jsonl"):
            return "transcript"
        return "tool-result"
    if name == "audit.jsonl":
        return "audit"
    if name == ".audit-key":
        return "audit-key"
    return "output"


def find_transcript(session_dir: Path, session_id: str, cli: str | None):
    projects = session_dir / ".claude" / "projects"
    if not projects.is_dir() or not cli:
        return None, None
    dirs = [d for d in projects.iterdir() if d.is_dir()]
    uuid_part = session_id[len("local_"):]
    enc = next((d for d in dirs if uuid_part in d.name), dirs[0] if dirs else None)
    if enc is None:
        return None, None
    jsonl = enc / f"{cli}.jsonl"
    return (enc.name, jsonl if jsonl.is_file() else None)


# --- pack ---

def pack(profile: Path, space: dict, out_root: Path, vm_files: Path | None, force: bool) -> Path:
    slug = slugify(space.get("name", "project"))
    bundle = out_root / f"{slug}.coworkbundle"
    if bundle.exists():
        if not force:
            sys.exit(f"{bundle} already exists; pass --force to overwrite.")
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)

    space_id = space["id"]
    sessions_meta: list[dict] = []
    warnings: list[str] = [
        "Credentials (.credentials.json) and mcp-needs-auth-cache.json are not "
        "included; the destination Cowork re-auths MCP tools on the same account."
    ]
    vm_missing: list[str] = []
    no_transcript: list[str] = []

    for sidecar_path in sorted(profile.glob("local_*.json")):
        if not SIDECAR_RE.match(sidecar_path.name):
            continue
        side = json.loads(sidecar_path.read_text(encoding="utf-8"))
        if side.get("spaceId") != space_id:
            continue

        session_id = sidecar_path.stem
        session_dir = profile / session_id
        cli = side.get("cliSessionId")
        vm = side.get("vmProcessName")
        dest = bundle / "sessions" / session_id
        dest.mkdir(parents=True)

        shutil.copy2(sidecar_path, dest / "sidecar.json")

        enc_name, transcript = find_transcript(session_dir, session_id, cli)
        t_bytes = t_compactions = 0
        vm_ref = False
        if transcript is not None:
            (dest / "transcript").mkdir(parents=True, exist_ok=True)
            shutil.copy2(transcript, dest / "transcript" / f"{cli}.jsonl")
            nested = transcript.parent / cli
            if nested.is_dir():
                shutil.copytree(nested, dest / "transcript" / cli, dirs_exist_ok=True)
            t_bytes, t_compactions, vm_ref = scan_transcript(transcript, vm)
        else:
            no_transcript.append(session_id)

        for sub in ("outputs", "uploads"):
            src = session_dir / sub
            if src.is_dir() and any(src.iterdir()):
                shutil.copytree(src, dest / sub, dirs_exist_ok=True)

        for audit in (session_dir / "audit.jsonl", session_dir / ".audit-key"):
            if audit.is_file():
                shutil.copy2(audit, dest / audit.name)

        vm_included = False
        if vm_files and vm:
            vm_src = vm_files / vm
            if vm_src.is_dir():
                shutil.copytree(vm_src, dest / "vm-files", dirs_exist_ok=True)
                vm_included = True
        if vm_ref and not vm_included:
            vm_missing.append(session_id)

        sessions_meta.append({
            "sessionId": session_id,
            "cliSessionId": cli,
            "title": side.get("title") or side.get("name") or "(untitled)",
            "vmProcessName": vm,
            "encodedCwd": enc_name,
            "cwd": side.get("cwd"),
            "userSelectedFolders": side.get("userSelectedFolders", []),
            "fsDetectedFiles": side.get("fsDetectedFiles", []),
            "compactBoundaryCount": t_compactions,
            "transcriptBytes": t_bytes,
            "hasTranscript": transcript is not None,
            "vmReferenced": vm_ref,
            "vmFilesIncluded": vm_included,
        })

    # space entry + (non-empty) space memory
    (bundle / "space").mkdir()
    (bundle / "space" / "spaces-entry.json").write_text(
        json.dumps(space, indent=2), encoding="utf-8")
    mem = profile / "spaces" / space_id / "memory"
    if mem.is_dir() and any(mem.iterdir()):
        shutil.copytree(mem, bundle / "space" / "memory", dirs_exist_ok=True)

    if no_transcript:
        warnings.append(f"{len(no_transcript)} session(s) have a sidecar but no "
                        f"transcript on disk: {', '.join(no_transcript)}")
    if vm_missing:
        warnings.append(f"{len(vm_missing)} session(s) reference VM-internal paths "
                        f"whose files were not extracted; re-pack with --vm-files "
                        f"after vhdx-extract: {', '.join(vm_missing)}")

    root_name = profile.parent.parent.name
    manifest = {
        "schemaVersion": 1,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "bundleType": "cowork-project",
        "source": {
            "os": "windows" if sys.platform == "win32" else "macos",
            "user": Path.home().name,
            "home": str(Path.home()),
            "base": str(default_base()),
            "sessionsRootName": root_name,
            "pathSep": "\\" if sys.platform == "win32" else "/",
            "account": profile.parent.name,
            "profile": profile.name,
        },
        "project": {
            "spaceId": space_id,
            "name": space.get("name"),
            "slug": slug,
            "linkedProjectUuid": (space.get("projects") or [{}])[0].get("uuid"),
            "folders": [f.get("path") for f in space.get("folders", [])],
        },
        "sessions": sessions_meta,
        "components": [
            {
                "path": p.relative_to(bundle).as_posix(),
                "kind": classify(p.relative_to(bundle).as_posix()),
                "portability": "vm" if "/vm-files/" in p.relative_to(bundle).as_posix() else "host",
                "bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            }
            for p in sorted(bundle.rglob("*"))
            if p.is_file() and p.name != "manifest.json"
        ],
        "warnings": warnings,
    }
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return bundle


def main() -> None:
    ap = argparse.ArgumentParser(description="Pack a Cowork project into a .coworkbundle.")
    ap.add_argument("project", help="Project name (case-insensitive) or spaceId.")
    ap.add_argument("--out", type=Path, default=Path.home() / "cowork-bundles",
                    help="Output directory (default: ~/cowork-bundles).")
    ap.add_argument("--base", type=Path, help="Claude support dir (default: per-OS).")
    ap.add_argument("--vm-files", type=Path,
                    help="Pre-extracted VM tree (<vmProcessName>/...) to include.")
    ap.add_argument("--force", action="store_true", help="Overwrite an existing bundle.")
    args = ap.parse_args()

    base = args.base or default_base()
    key = args.project.strip().lower()
    for profile in find_profiles(base):
        spaces = load_spaces(profile)
        match = next((s for s in spaces
                      if s.get("id") == args.project or s.get("name", "").lower() == key), None)
        if match:
            bundle = pack(profile, match, args.out, args.vm_files, args.force)
            m = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
            total = sum(c["bytes"] for c in m["components"])
            print(f"Packed {m['project']['name']!r} -> {bundle}")
            print(f"  {len(m['sessions'])} sessions, {len(m['components'])} files, "
                  f"{total/1_048_576:.1f} MB")
            for w in m["warnings"]:
                print(f"  warning: {w}")
            return
    sys.exit(f"No project matching {args.project!r} found under {base}.")


if __name__ == "__main__":
    main()
