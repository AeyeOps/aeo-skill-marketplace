#!/usr/bin/env python3
"""
Rewrite absolute paths inside a Cowork sidecar or JSONL transcript.

Designed to be edited per migration: fill in SRC_USER, DST_USER, VM_NAME, and
the RULES list below with the source→dest mappings for this specific migration,
then run:

    python rewrite-paths.py <file>           # rewrite one file in-place
    python rewrite-paths.py --count <file>   # dry-run: report matches only
    python rewrite-paths.py --dir <dir>      # rewrite every *.json and *.jsonl
                                             #   recursively under <dir>

A timestamped backup is written alongside each rewritten file the first time
this script touches it (e.g. file.jsonl.bak1), so repeated runs are safe. Pass
--no-backup to disable.

Why Python (not Perl / sed):
- We operate on raw bytes. JSONL files contain JSON-escaped Windows paths
  where each directory separator is stored as the literal two-byte sequence
  `\\\\` (backslash backslash). Byte-level substitution avoids the double-
  escaping confusion that plagues Perl regex and shell sed.
- Compiled patterns are reused across files, so rewriting 16 files is fast.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# EDIT THIS SECTION FOR THE SPECIFIC MIGRATION
# ---------------------------------------------------------------------------

SRC_USER = "srcuser"            # username on the source Windows machine
DST_USER = "dstuser"            # username on the dest Windows machine
VM_NAME = "happy-magical-xxx"   # vmProcessName from the session's sidecar

# Where did you extract the VM's /sessions/<VM_NAME>/ files to on the dest?
# This becomes the rewrite target for any /sessions/<VM_NAME>/... reference
# that isn't already covered by a more specific mnt/ rule below.
VM_FILES_DEST = rf"C:\Users\{DST_USER}\cowork-archive\{VM_NAME}"

# JSON-escaped double backslash. Inside a JSONL file, a Windows path
# separator is stored as two literal backslash bytes, which becomes the
# four-char sequence \\\\ when you write it as a Python string literal.
BS = "\\\\"


def to_json_win(path: str) -> str:
    """Convert a Windows path to the form it appears in inside JSON strings,
    i.e. each real backslash becomes two literal backslash bytes."""
    return path.replace("\\", BS)


def unix_tail_to_json_win(tail: str) -> str:
    """Convert a Unix-style tail captured from a /sessions/.../TAIL match into
    the JSON-escaped Windows form (forward slashes become double backslashes)."""
    return tail.replace("/", BS)


# Rules run top-to-bottom. Each rule is either:
#   ("literal", src_bytes, dst_bytes)
#       Pure byte-for-byte substring replacement. No regex.
#   ("regex", compiled_pattern, repl_func)
#       repl_func is called with the re.Match and returns the replacement
#       string. Use this for VM-path rewrites where the tail is variable.
#
# The order matters: put more-specific mnt/ rules before the generic
# /sessions/<VM>/ catch-all, otherwise the catch-all will shadow them.

def _vm_mnt_rewrite(dest_prefix: str):
    """Build a re.sub replacement that rewrites
       /sessions/<VM_NAME>/mnt/<mount>/TAIL  ->  <dest_prefix>\\TAIL
    with TAIL's forward slashes converted to JSON double-backslash."""
    def repl(m: re.Match) -> str:
        tail = m.group(1) or ""
        return to_json_win(dest_prefix) + (BS + unix_tail_to_json_win(tail) if tail else "")
    return repl


def _vm_root_rewrite(dest_prefix: str):
    """Build a re.sub replacement for the /sessions/<VM_NAME>/TAIL catch-all."""
    def repl(m: re.Match) -> str:
        tail = m.group(1) or ""
        return to_json_win(dest_prefix) + (BS + unix_tail_to_json_win(tail) if tail else "")
    return repl


def _require_edited():
    if SRC_USER == "srcuser" or DST_USER == "dstuser" or VM_NAME == "happy-magical-xxx":
        raise SystemExit(
            "rewrite-paths.py has not been edited for this migration.\n"
            "Fill in SRC_USER, DST_USER, VM_NAME, VM_FILES_DEST, and the RULES\n"
            "list at the top of this file before running it."
        )


_require_edited()


RULES: list = [
    # Rule 1: source username in Windows paths (JSON-escaped form, i.e. `\\`
    # between each directory). This is the most common rewrite — always on.
    ("literal",
     f"Users{BS}{SRC_USER}{BS}",
     f"Users{BS}{DST_USER}{BS}"),

    # Rule 2: source username in forward-slash form (appears in assistant prose
    # like "I saw Users/srcuser/foo"). Cheap to include.
    ("literal",
     f"Users/{SRC_USER}/",
     f"Users/{DST_USER}/"),

    # Rule 3+: VM mnt bind-mount subdirs. Add one entry per mount the source
    # session had. Each `userSelectedFolders` entry produces a bind mount at
    # /sessions/<VM_NAME>/mnt/<folder-basename>/. Uncomment and edit for the
    # mounts relevant to THIS session.
    #
    # Example for a `C:\Users\<src>\dls` selected folder that should map to
    # `C:\Users\<dst>\dls` on the dest:
    # ("regex",
    #  re.compile(rf"/sessions/{re.escape(VM_NAME)}/mnt/dls/([A-Za-z0-9_./\-]*)"),
    #  _vm_mnt_rewrite(rf"C:\Users\{DST_USER}\dls")),
    #
    # Example for a `C:\Users\<src>\data\OneDrive\temp-from-vault` entry:
    # ("regex",
    #  re.compile(rf"/sessions/{re.escape(VM_NAME)}/mnt/temp-from-vault/([A-Za-z0-9_./\-]*)"),
    #  _vm_mnt_rewrite(rf"C:\Users\{DST_USER}\data\OneDrive\temp-from-vault")),

    # Catch-all for everything else under /sessions/<VM_NAME>/. Must come
    # AFTER the mnt/ rules so it doesn't shadow them. Rewrites to wherever
    # you extracted VM files on the dest.
    ("regex",
     re.compile(rf"/sessions/{re.escape(VM_NAME)}/([A-Za-z0-9_./\-]*)"),
     _vm_root_rewrite(VM_FILES_DEST)),

    # Bare /sessions/<VM_NAME> with no trailing slash.
    ("literal",
     f"/sessions/{VM_NAME}",
     to_json_win(VM_FILES_DEST)),
]


# ---------------------------------------------------------------------------
# Engine (no need to edit below)
# ---------------------------------------------------------------------------


def apply_rules(content: str) -> tuple[str, dict]:
    """Apply every rule to the content and return (new_content, stats)."""
    stats: dict[str, int] = {}
    new = content
    for rule in RULES:
        kind = rule[0]
        if kind == "literal":
            _, src, dst = rule
            count = new.count(src)
            if count:
                new = new.replace(src, dst)
            stats[f"literal:{src[:40]}"] = count
        elif kind == "regex":
            _, pattern, repl = rule
            new, count = pattern.subn(repl, new)
            stats[f"regex:{pattern.pattern[:40]}"] = count
        else:
            raise ValueError(f"unknown rule kind: {kind}")
    return new, stats


def next_backup_path(p: Path) -> Path:
    i = 1
    while True:
        cand = p.with_suffix(p.suffix + f".bak{i}")
        if not cand.exists():
            return cand
        i += 1


def process_file(path: Path, *, dry_run: bool, backup: bool) -> None:
    content = path.read_text(encoding="utf-8")
    before = len(content)
    new, stats = apply_rules(content)
    total = sum(stats.values())

    if dry_run:
        print(f"{path} [dry-run] {total} matches")
        for k, v in stats.items():
            if v:
                print(f"  {v:6d}  {k}")
        return

    if total == 0:
        print(f"{path}: 0 matches, unchanged")
        return

    if backup:
        bpath = next_backup_path(path)
        bpath.write_bytes(path.read_bytes())
        print(f"  backup -> {bpath.name}")

    path.write_text(new, encoding="utf-8")
    after = len(new)
    print(f"{path}: {before} -> {after} bytes ({after - before:+d}), {total} matches")
    for k, v in stats.items():
        if v:
            print(f"  {v:6d}  {k}")


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("file", nargs="?", help="file to rewrite in place")
    g.add_argument("--dir", help="rewrite every *.json and *.jsonl under dir")
    ap.add_argument("--count", action="store_true", help="dry run, report only")
    ap.add_argument("--no-backup", action="store_true", help="skip .bakN backup")
    args = ap.parse_args()

    targets: list[Path] = []
    if args.dir:
        root = Path(args.dir)
        if not root.is_dir():
            print(f"not a directory: {root}", file=sys.stderr)
            return 2
        targets.extend(sorted(root.rglob("*.json")))
        targets.extend(sorted(root.rglob("*.jsonl")))
    else:
        targets.append(Path(args.file))

    for t in targets:
        if not t.is_file():
            print(f"skip (not a file): {t}", file=sys.stderr)
            continue
        process_file(t, dry_run=args.count, backup=not args.no_backup)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
