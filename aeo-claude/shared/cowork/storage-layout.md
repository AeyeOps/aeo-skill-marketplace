# Cowork on-disk storage layout (Windows and macOS)

The durable facts about where Claude Cowork keeps session data, and how the
pieces reference each other. Read this before running any of the cowork skills
(migrate, export, import, inspect): the path-rewrite, sidecar-restore, and
enumeration steps all assume you know these structures.

Cowork stores everything as local files (it is not server-backed), which is why
file-level export/import works at all. The layout is the same on Windows and
macOS apart from the base directory and the host-path string form; the
cross-platform mapping is in the last section.

## Where the profile lives

```
Windows base: ~\AppData\Roaming\Claude\            (i.e. $env:APPDATA\Claude)
macOS   base: ~/Library/Application Support/Claude/
```

Under the base, each profile lives at:

```
<base>/local-agent-mode-sessions/<account-uuid>/<profile-uuid>/
```

Two detection notes:

- On macOS, build 1.1.4498 (2026-02-27) renamed `local-agent-mode-sessions/` to
  `claude-code-sessions/` with no migration. Detect **both** names.
- The account UUID and profile UUID are the same on every machine logged into the
  same Cowork account. Discover them by enumerating the two directory levels; do
  not hardcode them, and when migrating, drop files into the identical path on the
  destination.

## The space registry: `spaces.json` (authoritative project list)

`spaces.json` at the profile root is the source of truth for the "projects" shown
in the Cowork left nav. It is a single object with a top-level `spaces` array;
each entry has:

- `id` — the space UUID (a session links to it via the sidecar's `spaceId`).
- `name` — the display name (this is what the UI calls the project).
- `folders[].path` — host folders bound to the project (absolute OS paths).
- `projects[].uuid` — a linked synced-knowledge Project, present **only** when the
  project knowledge cache has been hydrated. Many spaces have `projects: []`.
- `links[]`, `createdAt`, `updatedAt`.

**Count projects from `spaces.json`, never from the `spaces/` subdirectory or
`.project-cache/`.** Those two are created lazily and undercount. Observed on a
live profile: 6 spaces in `spaces.json` versus 3 dirs in `spaces/` and 1 in
`.project-cache/`.

Terminology that is easy to conflate: a **space** is the project container
(`id` + `name` + `folders` + sessions). A **`projects[].uuid`** is the separate
UUIDv7 of a synced claude.ai-style knowledge Project that hydrates
`.project-cache/<projectUuid>/`. A space may have zero or one.

**Parsing gotcha:** a sidecar (and some Cowork JSON) can contain a property whose
key is the empty string. In PowerShell you must use `ConvertFrom-Json -AsHashtable`
or it throws `property whose name is an empty string`. Python's `json.load`
handles it without special flags.

## The two session IDs

A session has two distinct IDs, and conflating them is the most common migration
mistake:

- `sessionId` = `local_<uuid>` — names the sidecar file and the session working
  directory.
- `cliSessionId` = a different UUID — names the JSONL transcript file.

## Per-session files

Under the profile directory, for each session:

- `local_<uuid>.json` — the **sidecar**. Holds session metadata
  (`userSelectedFolders`, `spaceId`, `cliSessionId`, `vmProcessName`,
  `initialMessage`, `systemPrompt`, the enabled MCP tool list, and more) and
  populates the session list and the scratchpad in the UI. Cowork may leave
  `.bak*` / `.orig` siblings next to it; skip those when enumerating (match
  `local_<uuid>.json` exactly). Three of its fields matter for a path rewrite:
  - `spaceId` — links the session to a `spaces.json` entry. Absent or empty for an
    **orphan** session not attached to any project (such a session has no
    `spaces/<spaceId>/memory` or `.project-cache` component to carry).
  - `cwd` — the session's host-side outputs scratchpad, of the form
    `.../local-agent-mode-sessions/<acct>/<prof>/local_<uuid>/outputs`. A real host
    path. It is **not** a `/sessions/<vm>/...` VM path; those appear only in
    transcript-event `cwd` values, never in the sidecar's top-level `cwd`.
  - `fsDetectedFiles` — an array of `{hostPath, fileName, timestamp}` objects, each
    `hostPath` an absolute host path. Easy to miss because it is not a folder field.
- `local_<uuid>/.claude/projects/<encoded-cwd>/<cliSessionId>.jsonl` — the actual
  transcript, one JSON event per line.
- `local_<uuid>/.claude/projects/<encoded-cwd>/<cliSessionId>/subagents/agent-<id>.jsonl`
  — subagent and compaction-summary transcripts. Each `agent-<id>.jsonl` is
  **paired with** an `agent-<id>.meta.json` descriptor; carry both or the subagent
  renders incompletely.
- `local_<uuid>/outputs/**` — host-side files the agent wrote to its scratchpad
  (the directory the sidecar `cwd` points at).
- `local_<uuid>/.claude/` — per-session Claude Code config and state
  (`.claude.json`, `.credentials.json`, `mcp-needs-auth-cache.json`, `backups/`).
  Copyable, but `.credentials.json` and `mcp-needs-auth-cache.json` are
  machine/account-bound: expect re-auth on the destination rather than a literal copy.
- `local_<uuid>/audit.jsonl` (+ `.audit-key`) — a per-session tamper-evident audit
  trail. Plain files, portable as-is.

## Per-space and profile-level files

- `spaces/<spaceId>/memory/*.md` — persistent per-space memory (`MEMORY.md` plus
  `feedback_` / `project_` / `reference_` markdown) shared by all sessions whose
  sidecar `spaceId` matches. Only exists for space-attached sessions.
- `.project-cache/<projectUuid>/` — cached synced project knowledge for a space's
  `projects[].uuid` (`docs/`, `files/`, `memory.md`, `metadata.json`,
  `syncs.json`). **Derived**: regenerated from the project's source folders on
  first open, so it can be omitted from an export and re-synced.
- `agent/` — profile-level "ditto" agent state (`local_ditto_<prof>.json`,
  `memory/`), shared across the whole profile rather than per-session.

## The VM filesystem

Cowork runs Claude Code inside a lightweight VM. Per-session working directories
`/sessions/<vmProcessName>/` live in a persistent ext4 image at:

```
<base>/vm_bundles/claudevm.bundle/sessiondata.vhdx
```

The image is shared across all sessions; each session gets a subdirectory named by
its `vmProcessName`. Files the agent created inside `/sessions/<vmProcessName>/`
that were never written to a host-mounted folder exist only here; recover them by
mounting the image (see `vhdx-extract.md`). The sibling `rootfs.vhdx` is the Linux
OS image; do not touch it.

The in-image `/sessions/<vmProcessName>/` layout is identical across platforms, but
the **runtime and mount tooling differ**: Windows uses WSL2 + Hyper-V (`wsl --mount`);
macOS uses Apple's Virtualization.framework. That split lives in `vhdx-extract.md`.

## Windows <-> macOS path mapping (for cross-platform import)

| Element | Windows | macOS |
|---|---|---|
| base support dir | `~\AppData\Roaming\Claude` | `~/Library/Application Support/Claude` |
| sessions root dir name | `local-agent-mode-sessions` | `local-agent-mode-sessions` or `claude-code-sessions` (post 1.1.4498) |
| host path form | `C:\Users\<u>\...` (backslash) | `/Users/<u>/...` (forward slash) |
| separator in JSONL strings | escaped double-backslash bytes | single forward slash |
| encoded-cwd dir name | `C--Users-<u>-...` | `-Users-<u>-...` (regenerate from the rewritten cwd; do not edit the name in place) |
| VM runtime | WSL2 + Hyper-V | Virtualization.framework |

The encoded-cwd directory name is a flattened encoding of the absolute `cwd`, so it
changes per machine. On import you **rename** that directory to match the rewritten
cwd rather than rewriting the string inside it. Account and profile UUIDs do not
change across machines on the same login, so they are never rewritten.

## Sidecar rewrite on first load

Cowork rewrites the sidecar the first time it loads a session, stripping any
`userSelectedFolders` entry whose path does not exist on the current machine. This
is why a migration or import stashes a pristine copy of the source sidecar before
letting Cowork open the session: you re-apply it after the destination folders
physically exist (see the cowork-migrate / cowork-import SKILL.md restore step).
