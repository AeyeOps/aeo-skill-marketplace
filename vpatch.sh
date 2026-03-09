#!/usr/bin/env bash
set -euo pipefail

BINARY="$HOME/.local/share/claude/versions/2.1.71"
BACKUP="$BINARY.bak"
PATCHED="$BINARY.patched"

for f in "$BINARY" "$BACKUP" "$PATCHED"; do
  if [[ ! -f "$f" ]]; then
    echo "MISSING: $f"
    exit 1
  fi
done

hash_active=$(sha256sum "$BINARY"   | awk '{print $1}')
hash_bak=$(sha256sum "$BACKUP"      | awk '{print $1}')
hash_patch=$(sha256sum "$PATCHED"   | awk '{print $1}')

echo "active:  $hash_active"
echo "backup:  $hash_bak"
echo "patched: $hash_patch"
echo

if [[ "$hash_bak" == "$hash_patch" ]]; then
  echo "ERROR: backup and patched have the same hash — something is wrong"
  exit 1
fi

if [[ "$hash_active" == "$hash_patch" ]]; then
  echo "Already patched — nothing to do."
  exit 0
elif [[ "$hash_active" == "$hash_bak" ]]; then
  echo "Active binary matches backup (original) — auto-updater likely overwrote the patch."
  echo "Restoring patched version..."
  cp "$PATCHED" "$BINARY"
  chmod 755 "$BINARY"
  echo "Done. Restart Claude Code for the patch to take effect."
else
  echo "WARNING: Active binary matches neither backup nor patched."
  echo "This may be a new version from auto-update."
  read -rp "Overwrite with patched version anyway? [y/N] " ans
  if [[ "${ans,,}" == "y" ]]; then
    cp "$PATCHED" "$BINARY"
    chmod 755 "$BINARY"
    echo "Done. Restart Claude Code for the patch to take effect."
  else
    echo "Aborted."
    exit 1
  fi
fi
