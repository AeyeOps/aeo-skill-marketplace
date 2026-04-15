---
name: cowork-migrate
description: |
  Migrate a Claude Cowork session from one Windows machine to another with full
  history, working file links, and no truncated-transcript rendering bug. Use this
  whenever the user mentions moving, importing, copying, or migrating a Cowork
  session/conversation/project between machines — or troubleshoots symptoms of a
  broken import like "session shows blank", "only 32 messages showing", "scratchpad
  files don't open", "can't scroll past latest compaction", or "Loaded N messages
  (truncated via tail/compaction)" in the Cowork log. Covers orphan sessions on
  Windows→Windows (same Cowork account). Handles the undocumented two-layer
  compact_boundary truncation filter in app.asar that silently clips imported
  transcripts. Spaces/Projects and cross-platform are out of scope for this iteration.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
---

# cowork-migrate

Migrate one Claude Cowork session from a source Windows machine to a destination
Windows machine so that the full transcript renders, file links resolve, and the
scratchpad metadata survives Cowork's first-load sidecar rewrite.

This skill is **rigid**: the truncation-filter workaround in particular has a narrow
winning configuration, and skipping steps produces subtle partial-history bugs that
look like success. Follow the workflow in order.

## When this skill applies

Trigger on any of:
- Explicit intent: "migrate my cowork session/conversation/project from X to Y",
  "import this cowork session", "bring my cowork work over", "copy cowork from
  my laptop to my desktop"
- Symptom reports after a manual copy attempt:
  - Session visible in list but opens blank
  - Scratchpad shows reviewed files but clicks go nowhere
  - History cuts off at last compaction; older messages missing
  - Log shows `Loaded N messages from transcript ... (truncated via tail)` or
    `(truncated via compaction)`
  - Log shows `Transcript not found` or `Filtering out deleted folder`
- Questions about Cowork storage layout, sidecars, `local_<uuid>.json`,
  `sessiondata.vhdx`, `compact_boundary`, `preservedSegment`

If the user is asking about Spaces/Projects (multi-session containers), Linux or
Mac Cowork, or cross-account migration, say so — this iteration does not cover
those and a different workflow is required.

## Preconditions

- Both machines run Claude Cowork for Windows and are logged into the **same Cowork
  account** (account UUID and profile UUID must match — they're identical across
  machines for the same login, so you do not invent new IDs).
- You can reach the source machine via SSH or have its files locally already.
- The user has agreed to **quit Cowork on the source machine** — the
  `sessiondata.vhdx` is locked while Cowork is running.
- You have the session's friendly title or `cliSessionId` prefix so you can
  disambiguate.

## Key facts (read before acting)

- Each Cowork profile lives at
  `C:\Users\<user>\AppData\Roaming\Claude\local-agent-mode-sessions\<account-uuid>\<profile-uuid>\`.
  Account and profile UUIDs are **the same on every machine** logged into the same
  account — drop files into the identical path, do not rename.
- A session consists of **two distinct IDs**:
  - `sessionId` = `local_<uuid>` — the sidecar filename and the working dir name
  - `cliSessionId` = a different UUID — names the JSONL transcript file
  Don't conflate them.
- Per-session files in the profile dir:
  - `local_<uuid>.json` — sidecar (metadata, `userSelectedFolders`, `spaceId`,
    `cliSessionId`, `initialMessage`, `systemPrompt`, MCP tool list, etc.).
    Populates the session list and scratchpad. ~180 KB.
  - `local_<uuid>/.claude/projects/<encoded-cwd>/<cliSessionId>.jsonl` — the
    actual transcript, one event per line.
  - `local_<uuid>/.claude/projects/<encoded-cwd>/<cliSessionId>/subagents/*.jsonl`
    — subagent and compaction-summary transcripts.
- Cowork runs Claude Code inside a VM (WSL2+Hyper-V). Session working dirs
  `/sessions/<vmProcessName>/` live in a persistent ext4 image at
  `C:\Users\<user>\AppData\Roaming\Claude\vm_bundles\claudevm.bundle\sessiondata.vhdx`.
  Files the agent created inside `/sessions/<vmProcessName>/` (and not in a
  host-mounted dir) only exist there — you extract them by mounting the VHDX.
- Cowork **rewrites the sidecar on first load**, stripping
  `userSelectedFolders` entries whose paths don't exist on the destination. Always
  stash a pristine copy of the source sidecar before dropping anything in the dest
  profile so you can re-apply it after the dest folders physically exist.
- **The truncation filter.** Cowork's UI only renders messages after the last
  `compact_boundary` event, using a two-layer filter in `app.asar`. Naively copying
  a transcript with N compactions yields only the events after the most recent one.
  Fixing this requires (a) ensuring the last 30 MB of the file contains a
  `compact_boundary` line with a populated `compactMetadata.preservedSegment` so the
  file reader loads the full file, and (b) stitching each boundary's `parentUuid`
  so the walker can traverse from `tailUuid` back to `headUuid`. Full details and
  the pseudocode from `app.asar` live in `references/truncation-filter.md` — read
  that before touching the JSONL.

## Workflow

### 1. Inventory the source

Ask the source host for its sidecars and pick the right one by title. On Windows
via PowerShell locally, or remotely over SSH with `-EncodedCommand` to avoid
quoting pitfalls:

```powershell
$profile = "$env:APPDATA\Claude\local-agent-mode-sessions\<acct>\<prof>\"
Get-ChildItem $profile -Filter "local_*.json" | ForEach-Object {
    $j = Get-Content $_.FullName -Raw | ConvertFrom-Json
    [PSCustomObject]@{
        Id = $j.sessionId.Substring(6,8)
        Title = $j.title
        Folders = ($j.userSelectedFolders -join "|")
        VmName = $j.vmProcessName
        Cli = $j.cliSessionId
    }
}
```

Note the exact `sessionId`, `cliSessionId`, `vmProcessName`, and the list of
`userSelectedFolders`. You'll need all four.

### 2. Quit Cowork on the source

Confirm the user has quit Cowork so the `sessiondata.vhdx` lock releases. If you
skip this, `scp`/`cp` of the VHDX will either fail or capture a corrupt snapshot.

### 3. Pull the files

Three things to copy from source to destination:

1. **The sidecar**: `local_<uuid>.json`. Save two copies on the dest: one as a
   pristine reference (e.g. under `/tmp/` or `C:\Users\<dst>\cowork-archive\`), one
   to install into the profile directory after path rewriting.
2. **The transcript dir**: the entire `local_<uuid>/` directory, including
   `.claude/projects/<encoded-cwd>/<cliSessionId>.jsonl` and every
   `subagents/*.jsonl`. Copy it to the dest at the identical profile path.
3. **The VM session files**: mount `sessiondata.vhdx` read-only, extract files
   from `/sessions/<vmProcessName>/` that the user cares about (skip
   `node_modules`, `.cache`, `.local`, `.npm*` — those are junk). Write them to a
   well-known host directory on the dest, e.g.
   `C:\Users\<dst>\cowork-archive\<vmProcessName>\`. This becomes the rewrite
   target for broken `/sessions/<vmProcessName>/...` references.

   VHDX extraction (run on the dest machine after copying the VHDX there):
   ```
   wsl --mount --vhd 'C:\full\path\to\sessiondata.vhdx' --bare
   # inside WSL:
   lsblk                                           # find device (labeled `sessions`)
   mkdir -p /mnt/cowork-sessions
   mount -o ro /dev/sdX /mnt/cowork-sessions
   # copy files from /mnt/cowork-sessions/<vmProcessName>/ out to the host
   umount /mnt/cowork-sessions
   wsl --unmount 'C:\full\path\to\sessiondata.vhdx'
   ```

   If running WSL from git-bash, prefix the command with `MSYS_NO_PATHCONV=1` to
   stop the shell from rewriting `/mnt/c/...` arguments.

### 4. Rewrite paths in every JSONL + the sidecar

Transcripts reference absolute paths from the source machine. Four classes:

| Class | Pattern | Rewrite target |
|---|---|---|
| Source username in Windows paths | `C:\Users\<srcuser>\...` | Dest username |
| Source-specific folder layout | e.g. source has a junction or symlink that the dest lacks | Ask the user what the right dest path is |
| VM bind-mount paths | `/sessions/<vm>/mnt/<mountname>/...` | The real host dir the mount pointed at on source — **which is the folder whose basename matches `<mountname>`** in `userSelectedFolders`. E.g. a `userSelectedFolders` entry of `C:\Users\<srcuser>\Documents\work` produces a VM bind mount at `/sessions/<vm>/mnt/work`. Use that correspondence to discover what to rewrite to. |
| VM working-dir paths | `/sessions/<vm>/...` (often thousands of refs) | Wherever you extracted VM files to on the dest. Do **not** rewrite the `.claude/projects/-sessions-<vm>/` subdirectory name itself — that encoded-cwd string is the directory layout Cowork expects and stays unchanged. Only `cwd` **values** inside transcript event JSON get rewritten. |

Use `scripts/rewrite-paths.py` as a template. Copy it into a working dir, edit the
`SRC_USER`, `DST_USER`, `VM_NAME`, `VM_FILES_DEST`, and `RULES` constants at the
top for this migration's specific source→dest mappings, then run it against every
file that needs rewriting. The template ships with all rules **commented out** and
marked with placeholder usernames — you must uncomment the rules relevant to this
migration before running, otherwise the script is a no-op.

**Critical**: Cowork's file sandbox will only open files that live under an entry
in the sidecar's `userSelectedFolders`. After you decide where to stage the
extracted VM files (typically under `C:\Users\<dst>\cowork-archive\<vmname>\`),
you must **append that staging dir to `userSelectedFolders` in the rewritten
sidecar**, otherwise every click on a VM-origin file in the Cowork scratchpad
will warn `readLocalFile: path ... resolves outside allowed folders` and fail.
This is in addition to — not a replacement for — keeping the user's original
selected folders (dest-equivalent).

```
# dry run against one file to see matches before committing
python rewrite-paths.py --count path/to/local_<uuid>.json

# rewrite a single file in place (timestamped .bakN backup is written first)
python rewrite-paths.py path/to/<cliSessionId>.jsonl

# rewrite every *.json and *.jsonl under the session working dir in one shot
python rewrite-paths.py --dir path/to/local_<uuid>/
```

Apply the rewrite to every file: `local_<uuid>.json`, the main transcript JSONL,
and every `subagents/*.jsonl`. The script keeps backups so repeated runs are safe.

Why bytes matter: inside a JSONL file a Windows path separator is stored as two
literal backslash bytes, which appears as `\\\\` in a raw JSON string. The rewrite
script handles the escaping for you — as long as you write mappings in plain
Windows-path form (e.g. `rf"C:\Users\{DST_USER}\cowork-archive"`), the helpers
produce the right byte sequences. Do **not** try to hand-edit JSONL with
`grep '\\'` or `sed` — you'll miscount and miss references.

### 5. Restore the pristine sidecar's userSelectedFolders after first Cowork load

Start Cowork on the dest. The session appears in the list but Cowork will silently
strip any `userSelectedFolders` entries whose paths don't exist on the dest. This
is why step 3 stashed a pristine copy. Workflow:

1. Ensure the dest folders from the rewritten sidecar actually exist on disk.
   Create empty dirs if necessary, including the `cowork-archive/<vmname>`
   staging dir you added to `userSelectedFolders` in step 4.
2. Quit Cowork on the dest.
3. Copy the **rewritten pristine sidecar** over the one Cowork just mangled.
4. Restart Cowork.

**Filename convention for the two sidecar copies**: when you stash the source
sidecar in step 3, save it as
`<dst_archive>\<short-id>-pristine-sidecar.json` and keep it untouched. Save
the post-rewrite version as `<dst_archive>\<short-id>-rewritten-sidecar.json`.
The "pristine" name refers to "unmodified by Cowork's first-load rewrite", not
"unmodified by our path-rewrite script" — it's the pre-Cowork-mangle version we
want to put back in place, and it must have path rewrites applied before we put
it back.

### 6. Fix the compact_boundary truncation (skip if no boundaries)

**Fast path**: if the transcript JSONL has **zero** `compact_boundary` events
and is **≤ 50 MB**, you can skip this entire step. Cowork's layer-1 file reader
(`cDn`) reads the whole file in that case, and layer 2 (`lDn`) has no boundaries
to filter against, so every event loads. Quick check:

```
grep -c '"subtype":"compact_boundary"' <transcript>.jsonl    # want: 0
stat --printf='%s\n' <transcript>.jsonl                       # want: ≤ 52428800
```

`scripts/chain-walker.py` and `scripts/stitch-boundaries.py` both detect the
no-boundary case themselves and exit 0 with a "NO STITCH NEEDED" message, so
running them against a no-boundary transcript is safe and informative.

If the transcript has ≥1 `compact_boundary` event, continue below.

Even with the transcript in place, Cowork will likely show only messages after the
last compaction. The log signal is
`Loaded N messages from transcript for session <id> (truncated via compaction)` or
`(truncated via tail)` at
`C:\Users\<dst>\AppData\Roaming\Claude\logs\main.log`.

**Read `references/truncation-filter.md` before running the stitch script** — it
documents why the naive "just rename `compact_boundary`" hack breaks the file
reader (layer 1) even though it bypasses the event filter (layer 2), and why you
must stitch the `parentUuid` chain and populate `preservedSegment` instead.

Then run:

```
python scripts/chain-walker.py <transcript>.jsonl
```

This simulates Cowork's walker and reports whether it currently reaches `headUuid`.
If not (and it won't, on the first run), apply the fix:

```
python scripts/stitch-boundaries.py <transcript>.jsonl
```

It makes a `.bak5` backup, reverts any `compact_boundary_disabled` subtype, sets
each boundary's `parentUuid` to the most recent uuid-bearing event preceding it,
and adds `compactMetadata.preservedSegment: {headUuid, tailUuid}` to the **last**
boundary. Re-run `chain-walker.py` to confirm `WALK OK: head reached in N steps`.

Apply the fix to the main transcript. Subagent JSONLs in `subagents/` do not go
through this filter and do not need stitching.

### 7. Verify

1. Start Cowork on the dest and open the session.
2. Tail the log:
   `C:\Users\<dst>\AppData\Roaming\Claude\logs\main.log`
3. Look for `Loaded N messages from transcript for session <id>` **without** any
   `(truncated via ...)` suffix. The number will be below total JSONL line count —
   that's normal, Cowork filters `queue-operation`, `last-prompt`, `progress`,
   `attachment`, and `isVisibleInTranscriptOnly` events.
4. Scroll to the top of the conversation in the UI and confirm you see the first
   user message.
5. Click a referenced file path — it should open. Paths that still 404 are usually
   files that only ever lived inside the VM and were never persisted to a
   host-mounted dir; those are genuinely gone (note this to the user as expected
   data loss).

Absence of `(truncated via ...)` plus a full-range scroll is the success
criterion.

## Important gotchas

- **Cowork rewrites the sidecar on first load.** Always keep a pristine copy.
  See step 5.
- **Raw backslash escaping in JSONL is confusing.** Don't hand-edit with
  `sed`/`grep` — miscounts are common. Use `scripts/rewrite-paths.py` with its
  byte-aware rule engine.
- **Cowork creates boundary pairs with duplicate UUIDs.** In sessions with
  many compactions, the second boundary of pair N shares its UUID with the
  first boundary of pair N+1. The bundled `stitch-boundaries.py` detects
  this and assigns fresh UUIDs to later occurrences before stitching. If
  you see `chain-walker.py` report a cycle, run `stitch-boundaries.py`
  first — it handles dedup automatically.
- **Renaming `compact_boundary` is a red herring.** It gets layer 2 to return
  "keep everything" but makes layer 1 fall back to tail-only reading for any
  file >50 MB. Net result: partial history that looks like success. Use the
  stitch approach instead.
- **`isCompactSummary: true` is also a red herring.** It only hides an
  individual summary message in the rendered timeline. It does not affect
  either truncation layer. Don't waste time on it.
- **PowerShell 5.1 `Remove-Item` on junctions throws `NullReferenceException`.**
  Use `[System.IO.Directory]::Delete("C:\path", $false)` instead.
- **Files created inside the VM that were never persisted to a host-mounted
  dir are unrecoverable.** Click-to-open on those will 404 in the imported
  session. This is expected data loss, not a migration bug.

## What this skill does NOT cover (yet)

- Cowork Spaces/Projects (multi-session containers with shared memory and
  project-cache docs). Session linkage is via the `spaceId` field, and the
  `spaces/<space-uuid>/` and `.project-cache/<project-uuid>/` directories also
  need to come over. Iteration 2.
- Linux or macOS Cowork migrations.
- Cross-account migration (different Cowork accounts on source and dest —
  account and profile UUIDs differ and the sidecar's `sessionId` must be
  rewritten everywhere).

If the user asks for any of these, explain the scope and stop. Do not improvise.

## Bundled files

- `references/truncation-filter.md` — full reverse-engineered pseudocode of
  `cDn`, `sDn`, `iDn`, `lDn` from `app.asar`, the winning stitch configuration,
  and the two red-herring approaches that look like they work but don't.
- `scripts/stitch-boundaries.py` — fixes the transcript.
- `scripts/chain-walker.py` — validator that simulates Cowork's parentUuid walk
  and reports whether it reaches `headUuid`.
- `scripts/rewrite-paths.py` — template for path rewrites. Copy, edit the
  `SRC_USER`/`DST_USER`/`VM_NAME`/`RULES` constants for the specific migration,
  then run against every JSONL and the sidecar (or pass `--dir` to walk the
  whole session working dir in one shot).
