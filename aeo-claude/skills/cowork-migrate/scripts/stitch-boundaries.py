#!/usr/bin/env python3
"""
Stitch compact_boundary events' parentUuid into a continuous chain so that
Cowork's lDn walks from tailUuid back through every message and every
compact_boundary, eventually reaching headUuid.

- Detects and deduplicates boundary UUID collisions (Cowork creates boundary
  pairs where the second boundary of pair N shares its UUID with the first
  of pair N+1 — a simple uuid_map would create a cycle)
- Reverts subtype 'compact_boundary_disabled' -> 'compact_boundary'
- Sets parentUuid of each boundary to the nearest preceding uuid-bearing event
- Adds compactMetadata.preservedSegment {headUuid, tailUuid} to the LAST boundary
- Writes other lines back unchanged (byte-for-byte).

Exit codes:
  0  stitch applied successfully, or no stitch needed (0 boundaries, small file)
  1  cannot stitch (0 boundaries but file > 50 MB) or other error
  2  usage error
"""
import json, sys, os, shutil, uuid as uuid_mod
from collections import Counter

LAYER1_SIZE_LIMIT = 50 * 1024 * 1024  # Lwt / Fwt in cDn — 50 MB

if len(sys.argv) != 2:
    print("usage: stitch-boundaries.py <transcript.jsonl>", file=sys.stderr)
    sys.exit(2)

main = sys.argv[1]
size = os.path.getsize(main)

with open(main, 'rb') as f:
    lines = f.readlines()

print(f"file: {main}")
print(f"size: {size} bytes ({size / 1024 / 1024:.1f} MB)")
print(f"lines: {len(lines)}")

# First pass: find boundaries, their UUIDs, and non-boundary uuid-bearing events.
head_uuid = None
line_uuid = {}       # 0-based line idx -> uuid (non-boundary events only)
boundary_idxs = []   # 0-based line indices of boundary events
boundary_uuid = {}   # boundary line idx -> uuid from the JSON

for i, raw in enumerate(lines):
    try:
        j = json.loads(raw)
    except Exception:
        continue
    u = j.get('uuid')
    t = j.get('type')
    sub = j.get('subtype') or ''
    if 'compact_boundary' in sub:
        boundary_idxs.append(i)
        if u:
            boundary_uuid[i] = u
        continue
    if u:
        line_uuid[i] = u
        if head_uuid is None and t in ('user', 'assistant'):
            head_uuid = u

print(f"head_uuid: {head_uuid}")
print(f"boundary count: {len(boundary_idxs)}")

# Fast path: no boundaries at all
if not boundary_idxs:
    if size <= LAYER1_SIZE_LIMIT:
        print(f"NO STITCH NEEDED: transcript has 0 compact_boundary events and "
              f"is {size} bytes (<= {LAYER1_SIZE_LIMIT}). Layer 1 (cDn) reads "
              f"it whole, layer 2 (lDn) keeps every event by construction. "
              f"File left untouched.")
        sys.exit(0)
    else:
        print(f"CANNOT STITCH: transcript has 0 compact_boundary events BUT is "
              f"{size} bytes (> {LAYER1_SIZE_LIMIT}). Stitching needs at least "
              f"one boundary to anchor preservedSegment. This file will be "
              f"truncated via tail by layer 1 and there is nothing this script "
              f"can do about it.", file=sys.stderr)
        sys.exit(1)

# Detect duplicate boundary UUIDs. Cowork creates boundary pairs where the
# second boundary of pair N shares its UUID with the first boundary of pair
# N+1. A dict-based uuid_map would overwrite the earlier occurrence and the
# walker would cycle. Fix: assign fresh UUIDs to later occurrences.
uuid_counts = Counter(boundary_uuid.values())
dup_uuids = {u for u, c in uuid_counts.items() if c > 1}
if dup_uuids:
    print(f"duplicate boundary UUIDs detected: {len(dup_uuids)}")

uuid_remap = {}        # boundary line idx -> new uuid (for later occurrences)
msg_parent_updates = {}  # message line idx -> new parentUuid

for dup_uuid in dup_uuids:
    locs = sorted([i for i, u in boundary_uuid.items() if u == dup_uuid])
    # Keep the first occurrence, remap later ones
    for loc in locs[1:]:
        new = str(uuid_mod.uuid4())
        uuid_remap[loc] = new
        # Update messages whose parentUuid == dup_uuid and are closer to the
        # later occurrence than the earlier one
        midpoint = (locs[0] + loc) / 2
        for k, raw in enumerate(lines):
            if k in set(boundary_idxs):
                continue
            try:
                j = json.loads(raw)
            except Exception:
                continue
            if j.get('parentUuid') == dup_uuid and k > midpoint:
                msg_parent_updates[k] = new

if uuid_remap:
    print(f"boundary UUID remaps: {len(uuid_remap)}")
if msg_parent_updates:
    print(f"message parentUuid updates (for dedup): {len(msg_parent_updates)}")

# Compute final boundary UUIDs after remaps
final_boundary_uuid = {}
for bi in boundary_idxs:
    if bi in uuid_remap:
        final_boundary_uuid[bi] = uuid_remap[bi]
    elif bi in boundary_uuid:
        final_boundary_uuid[bi] = boundary_uuid[bi]

# Combined uuid map for finding preceding uuid of each boundary
all_uuid_by_line = dict(line_uuid)
all_uuid_by_line.update(final_boundary_uuid)

# Backup — only after confirming we have work to do
backup = main + ".bak5"
if not os.path.exists(backup):
    shutil.copy2(main, backup)
    print(f"backup: {backup}")

# For each boundary, find the uuid of the nearest preceding uuid-bearing event
prev_uuid_for_boundary = {}
for bi in boundary_idxs:
    best, best_line = None, -1
    for ln, u in all_uuid_by_line.items():
        if ln < bi and ln > best_line:
            best, best_line = u, ln
    prev_uuid_for_boundary[bi] = best

# tailUuid: last uuid-bearing non-boundary event before the last boundary
last_bi = boundary_idxs[-1]
tail_uuid = None
for k in range(last_bi - 1, -1, -1):
    if k in line_uuid:
        tail_uuid = line_uuid[k]
        break

print(f"tail_uuid (for last boundary): {tail_uuid}")

# Modify boundary lines
changed = 0
for bi in boundary_idxs:
    raw = lines[bi]
    j = json.loads(raw)
    orig_sub = j.get('subtype')

    if bi in uuid_remap:
        j['uuid'] = uuid_remap[bi]

    j['subtype'] = 'compact_boundary'

    prev = prev_uuid_for_boundary[bi]
    if prev:
        j['parentUuid'] = prev

    if bi == last_bi:
        cm = j.get('compactMetadata') or {}
        cm['preservedSegment'] = {'headUuid': head_uuid, 'tailUuid': tail_uuid}
        j['compactMetadata'] = cm

    new_raw = json.dumps(j, ensure_ascii=False, separators=(',', ':')).encode('utf-8') + b'\n'
    lines[bi] = new_raw
    changed += 1

# Modify messages with parent updates (dedup-related)
for mi, new_parent in msg_parent_updates.items():
    raw = lines[mi]
    j = json.loads(raw)
    j['parentUuid'] = new_parent
    new_raw = json.dumps(j, ensure_ascii=False, separators=(',', ':')).encode('utf-8') + b'\n'
    lines[mi] = new_raw
    changed += 1

print(f"modified {changed} lines ({len(boundary_idxs)} boundaries"
      f" + {len(msg_parent_updates)} dedup parent fixes)")
print(f"Last boundary preservedSegment: head={head_uuid} tail={tail_uuid}")

with open(main, 'wb') as f:
    f.writelines(lines)
print(f"wrote {main}")
