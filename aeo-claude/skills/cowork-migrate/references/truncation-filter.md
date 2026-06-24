# Cowork's two-layer compact_boundary truncation filter

This document explains the undocumented transcript truncation that Cowork's UI
applies when loading an imported session. Read this before running
`scripts/stitch-boundaries.py` — the winning configuration is narrow, and
two approaches that look correct on paper silently produce partial history.

Reverse-engineered from `app.asar` at
`C:\Program Files\WindowsApps\Claude_<version>\app\resources\app.asar`.
Function names (`cDn`, `sDn`, `iDn`, `lDn`) are the minified identifiers from
that bundle; they may change between releases, but the shape of the logic is
stable.

## The symptom

After successfully copying a session's sidecar and transcript to the dest
machine, Cowork shows a limited history: only messages after the most recent
compaction. The log at
`C:\Users\<user>\AppData\Roaming\Claude\logs\main.log`
contains one of:

- `Loaded N messages from transcript for session <id> (truncated via compaction)`
- `Loaded N messages from transcript for session <id> (truncated via tail)`
- (Winning) `Loaded N messages from transcript for session <id>` with no suffix

The `(truncated via ...)` suffix is the signal that one of the two truncation
layers below kicked in.

## Layer 1 — file reader (`cDn`)

Decides **how much of the JSONL file to read** and which "strategy" to log.

```js
function cDn(t) {
  const r = (await stat(t)).size;
  if (r <= Lwt) return {lines: readAll, strategy: "none"};     // <=50MB -> full file
  const {offset: n, hasPreservedSegment: i} = await sDn(t, r);  // scan last 30MB
  return n > 0 && i
    ? {lines: readAll, strategy: "none"}                        // WINNING branch
    : n > 0
      ? (r - n < Lwt
          ? {lines: readFromN, strategy: "compaction"}          // read from boundary
          : {lines: readTailBytes, strategy: "tail"})           // last 50MB from end
      : {lines: readTailBytes, strategy: "tail"};               // no boundary found
}
```

Key constants: `Lwt === Fwt === 50 * 1024 * 1024` (50 MB).

`sDn` reads the last 30 MB of the file, looks for the literal substring
`"compact_boundary"`, then calls `iDn` to strictly JSON-parse that line and
check `type === "system" && subtype === "compact_boundary"`. If the strict
check fails (e.g. because someone renamed the subtype to something clever),
the line is skipped.

The branch that yields `strategy: "none"` — i.e. the full file is loaded — only
fires when **both**:

1. At least one `compact_boundary` line is in the last 30 MB of the file, **and**
2. That boundary's JSON has `compactMetadata.preservedSegment` populated so that
   `sDn` sets `hasPreservedSegment === true`.

Miss either condition and you drop into one of the truncation branches below,
and Cowork logs the suffix that gives it away.

## Layer 2 — event filter (`lDn`)

Runs **after** the lines have been loaded. Walks forward through the events to
find the last boundary, then walks the `parentUuid` chain backward from the
preserved segment's `tailUuid` to build a set of uuids to keep.

```js
// First pass: locate the last compact_boundary in the loaded events.
r.reduce((u, d, f) => {
  if (d.type !== "system" || d.subtype !== "compact_boundary") return u;
  const p = d.compactMetadata?.preservedSegment;
  return p
    ? {absoluteLastBoundaryIdx: f, lastSeg: p, lastSegBoundaryIdx: f}
    : {...u, absoluteLastBoundaryIdx: f};
}, {absoluteLastBoundaryIdx: -1, lastSeg: void 0, lastSegBoundaryIdx: -1});

// Second pass: walk from preservedSegment.tailUuid via parentUuid, adding each
// visited uuid to a Set `c`. The walk stops on cycle, missing uuid, or on
// reaching preservedSegment.headUuid. If the walk does NOT reach headUuid,
// the Set is discarded and returned empty.
const l = lastSegBoundaryIdx >= 0 ? lastSegBoundaryIdx + 1 : 0;

// Final filter: keep an event iff
//   (idx >= l  OR  uuid is in the walked Set c)
//   AND NOT isCompactSummary
//   AND NOT isVisibleInTranscriptOnly
r.filter((u, d) => !(!(d >= l || u.uuid && c.has(u.uuid))
                     || u.isCompactSummary
                     || u.isVisibleInTranscriptOnly));
```

So to keep a pre-boundary message in the rendered timeline, its uuid must be
in the walked Set `c`. And `c` is only populated if the `tailUuid` → `headUuid`
walk succeeds.

Normally each `compact_boundary` event has `parentUuid: null` — boundaries are
logical roots, they don't parent anything. That means the walk from
`tailUuid` hits the next-older boundary, asks for its parent, gets `null`, and
stops. Set `c` is empty, no pre-boundary events are kept.

## The winning combination

To render the full transcript, **both** layers must cooperate:

1. **Layer 1**: the file reader must return `strategy: "none"`. For files
   ≤50 MB this happens automatically. For files >50 MB, the last 30 MB must
   contain a `compact_boundary` line with `compactMetadata.preservedSegment`
   populated.

2. **Layer 2**: the walk from `preservedSegment.tailUuid` must reach
   `preservedSegment.headUuid`. Since the walk only follows `parentUuid`
   pointers, every compaction boundary in the middle must be stitched: its
   `parentUuid` needs to point at the most recent uuid-bearing event
   immediately before it, so the chain is continuous all the way back to the
   first user/assistant message.

## The stitch procedure

For each `compact_boundary` event in the JSONL, rewrite its
`parentUuid: null` to the uuid of the most recent uuid-bearing event that
precedes that boundary line. Then, on the **last** boundary only, add:

```json
"compactMetadata": {
  "preservedSegment": {
    "headUuid": "<uuid of the first user/assistant message in the file>",
    "tailUuid": "<uuid of the last uuid-bearing event immediately before the last boundary>"
  }
}
```

After stitching, the walker traverses:
`tailUuid → events between the last two boundaries → second-to-last boundary →
 events between boundaries N-2 and N-1 → ... → first boundary → first user
 message → headUuid`.

Set `c` fills with every uuid in the chain. Layer 2's filter keeps everything.

`scripts/stitch-boundaries.py` implements this. `scripts/chain-walker.py`
simulates Layer 2's walk and reports whether `c` reaches `headUuid`; always
run the walker to validate before and after stitching.

## Red herring 1: flipping `isCompactSummary: false`

You'll see events marked `isCompactSummary: true`. These look like they might
be what's hiding the older history. They're not.

`isCompactSummary` is a **per-event cosmetic flag**. It hides an individual
compaction-summary message from the rendered timeline so you don't see the
model's "here's what we talked about" summary twice. Flipping it to `false`
changes which events appear **among the events Layer 2 already decided to keep**,
it does not change the set `c`. It does not affect Layer 1 at all.

Don't touch this field during migration. It has no bearing on the truncation
problem.

## Red herring 2: renaming `compact_boundary` to something Cowork doesn't recognize

Tempting shortcut: if the boundaries are the problem, rename their `subtype`
to `compact_boundary_disabled` (or similar) so Layer 2's "find the last
boundary" scan returns `-1`, sets `l = 0`, and the filter keeps every event.

This half-works on small files and fails on big ones. Here's why:

- **Layer 2 (good)**: `l = 0` means the filter condition `d >= l` is always
  true, so every event is kept. ✅
- **Layer 1 (bad)**: `sDn` scans the last 30 MB of the file for the literal
  substring `"compact_boundary"` and then strictly validates
  `subtype === "compact_boundary"`. A renamed subtype still contains the
  substring, but the strict check fails, so `sDn` treats those lines as
  "not a boundary" and keeps scanning. With no usable boundary found, `cDn`
  falls through to `strategy: "tail"` for any file >50 MB and reads only the
  **last 50 MB from the end of the file**. For a transcript with a long early
  history, that cuts off the start of the conversation. ❌

Net result: log says
`Loaded N messages from transcript ... (truncated via tail)` — a suffix that
looks like it's complaining about something else entirely, hiding the cause.

This approach only works if the entire transcript is already under 50 MB,
because then Layer 1 reads the whole file unconditionally. Don't rely on that
— do the stitch.

## Useful log lines for diagnosis

Filter `main.log` for:

- `Loaded \d+ messages from transcript` — success/failure signal
- `\(truncated via (tail|compaction)\)` — Layer 1 fell through
- `Transcript not found for session` — transcript path mismatch, Layer 1 not
  even running
- `Filtering out deleted folder` — `userSelectedFolders` stripped because the
  path doesn't exist on dest (see SKILL.md step 5)
- `Registration conflict (409)` — source Cowork is still holding the bridge
  registration; dest can view but not become live host until source
  disconnects

## Why this is narrow and brittle

Both function identifiers (`cDn`, `sDn`, `iDn`, `lDn`) and constant names
(`Lwt`, `Fwt`) are minifier-assigned and change between Cowork releases. The
**shape** of the two-layer filter (size-based file-reader strategy + walker
that requires `preservedSegment` + `parentUuid` continuity) is load-bearing
and has been stable so far, but if a future Cowork release breaks this
migration, start by re-extracting `app.asar` and searching for the
`compact_boundary` literal string to locate the new function names.
