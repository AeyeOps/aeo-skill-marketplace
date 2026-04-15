#!/usr/bin/env python3
"""
Simulate Cowork's lDn parentUuid walk over a transcript JSONL and report
whether the walk from preservedSegment.tailUuid reaches headUuid.

Exit codes:
  0  walk reached head (WALK OK) OR transcript has no compact_boundary events
     and is small enough that Cowork's layer 1 reads it whole (nothing to do)
  1  walk did not reach head (WALK PARTIAL) — stitch required
  2  usage error
"""
import json, os, sys

LAYER1_SIZE_LIMIT = 50 * 1024 * 1024  # Lwt / Fwt in cDn — 50 MB

if len(sys.argv) != 2:
    print("usage: chain-walker.py <transcript.jsonl>", file=sys.stderr)
    sys.exit(2)

main = sys.argv[1]
size = os.path.getsize(main)

# uuid -> (parentUuid, line_no, type/subtype)
# If duplicate UUIDs exist (Cowork creates boundary pairs sharing UUIDs),
# keep the LATER occurrence in the map — the walker walks backward from
# tail toward head, so the later (closer-to-tail) entry is the one it
# should follow first. We also count duplicates for a diagnostic warning.
uuid_map = {}
dup_count = 0
first_msg_uuid = None
last_boundary_line = None
last_uuid_before_last_boundary = None

with open(main, 'rb') as f:
    lines = f.readlines()

for i, raw in enumerate(lines, 1):
    try:
        j = json.loads(raw)
    except Exception:
        continue
    u = j.get('uuid')
    t = j.get('type')
    sub = j.get('subtype')
    if not u:
        continue
    p = j.get('parentUuid')
    if u in uuid_map:
        dup_count += 1
    uuid_map[u] = (p, i, t, sub)
    if first_msg_uuid is None and t in ('user', 'assistant'):
        first_msg_uuid = u

# Find line of last compact_boundary* event
for i, raw in enumerate(lines, 1):
    try:
        j = json.loads(raw)
    except Exception:
        continue
    sub = j.get('subtype') or ''
    if 'compact_boundary' in sub:
        last_boundary_line = i

# Fast path: no boundaries at all
if last_boundary_line is None:
    print(f"file: {main}")
    print(f"size: {size} bytes")
    print(f"total uuids: {len(uuid_map)}")
    print("compact_boundary events: 0")
    if size <= LAYER1_SIZE_LIMIT:
        print(f"NO STITCH NEEDED: transcript has 0 compact_boundary events and "
              f"is {size} bytes (<= {LAYER1_SIZE_LIMIT}). Layer 1 (cDn) reads "
              f"it whole, layer 2 (lDn) has no boundaries to filter against "
              f"and keeps every event by construction.")
        sys.exit(0)
    else:
        print(f"PROBLEM: transcript has 0 compact_boundary events BUT is "
              f"{size} bytes (> {LAYER1_SIZE_LIMIT}). Layer 1 will fall back "
              f"to tail-only reading — only the last {LAYER1_SIZE_LIMIT} bytes "
              f"load. There is nothing chain-walker can do about this; you need "
              f"a smaller transcript or an unrelated approach.")
        sys.exit(1)

# Find the last uuid whose line < last_boundary_line
for u, (p, ln, t, sub) in uuid_map.items():
    if ln < last_boundary_line:
        if last_uuid_before_last_boundary is None or ln > uuid_map[last_uuid_before_last_boundary][1]:
            last_uuid_before_last_boundary = u

print(f"first_msg_uuid (head): {first_msg_uuid}")
print(f"last boundary at line: {last_boundary_line}")
print(f"last uuid before boundary (tail): {last_uuid_before_last_boundary}")
if last_uuid_before_last_boundary:
    print(f"  (line {uuid_map[last_uuid_before_last_boundary][1]}, type {uuid_map[last_uuid_before_last_boundary][2]})")
print(f"total uuids: {len(uuid_map)}")
if dup_count:
    print(f"WARNING: {dup_count} duplicate UUID(s) detected — later occurrences "
          f"overwrite earlier ones in the map. If the walk cycles or breaks, "
          f"run stitch-boundaries.py first (it deduplicates before stitching).")

# Walk tail -> head via parentUuid
head = first_msg_uuid
tail = last_uuid_before_last_boundary
h = tail
seen = set()
steps = 0
hit = False
while h and h not in seen:
    seen.add(h)
    if h == head:
        hit = True
        break
    pe = uuid_map.get(h)
    if not pe:
        print(f"  CHAIN BREAK at step {steps}: uuid {h} not in map")
        break
    parent, ln, t, sub = pe
    if parent is None:
        print(f"  CHAIN END at step {steps}: uuid {h} (line {ln}, type {t}, subtype {sub}) has no parent")
        break
    h = parent
    steps += 1

if hit:
    print(f"WALK OK: head reached in {steps} steps, covers {len(seen)} messages")
    sys.exit(0)
else:
    print(f"WALK PARTIAL: {steps} steps, {len(seen)} messages reachable")
    sys.exit(1)
