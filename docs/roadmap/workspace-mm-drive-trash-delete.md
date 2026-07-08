# workspace-mm — Drive trash + permanent delete

## Problem

The AeyeOps `google_workspace_mcp` fork exposes Drive read/list/modify but has no tools for **moving files to Trash, emptying Trash, or permanently deleting files**. Users hit this gap whenever they need to purge accidentally-synced content (e.g. plaintext credentials uploaded by Drive Desktop before a `.gitignore` catches them) — they have to fall back to the Drive web UI, which an agent can't drive end-to-end.

Triggering use case: a `~/data/gdrive-mm/my-drive/macbook/` repo had stale plaintext credential files; deleting them locally pushed them to Drive Trash, where they sit for 30 days with full content recoverable. The agent could see them via `search_drive_files` with `trashed=true`, but couldn't purge them.

## Current capability

Working today via `mcp__workspace-mm__*`:
- `search_drive_files(q="trashed=true and …")` — finds trashed items
- `update_drive_file` — modifies metadata, but trash state is not exposed as a parameter
- No delete-anything tool

Drive REST API endpoints we'd need to wrap:
- `files.update(fileId, body={"trashed": true})` — soft delete (reversible)
- `files.update(fileId, body={"trashed": false})` — restore from trash
- `files.delete(fileId)` — permanent delete (must be on trashed file or it's a hard kill)
- `files.emptyTrash()` — purge all trashed items in one call

## Proposed tools

Three new tools, named to advertise destructiveness:

| Tool | Reversible? | Scope needed |
|---|---|---|
| `trash_drive_file` | yes — sets `trashed: true` | `drive` or `drive.file` |
| `restore_drive_file` | n/a — sets `trashed: false` | `drive` or `drive.file` |
| `delete_drive_file_permanent` | **no** | `drive` (full) — `drive.file` only allows delete on app-created files |
| `empty_drive_trash` | **no, all-at-once** | `drive` (full) |

The naming convention (`_permanent`, `empty_drive_trash`) is deliberate — agents read tool descriptions, and an unambiguous suffix reduces accidental invocation.

## Implementation considerations

### Scope upgrade

Today's OAuth consent likely includes `https://www.googleapis.com/auth/drive` (the read/write scope already covers metadata edits). Confirm the existing token claims it; if scoped narrower (`drive.file` only), the consent screen needs re-authorization before delete-permanent or empty-trash will work — those won't gracefully fall back, they'll 403.

### Confirmation gating

Both destructive tools should require an explicit `confirm` parameter that defaults to false. Pattern in spirit of the gmail-mm `delete_email`:

```python
@app.tool
def delete_drive_file_permanent(
    file_id: str,
    confirm: bool = False,
    user_google_email: str = ...,
):
    if not confirm:
        return {"error": "Permanent delete blocked — pass confirm=True"}
    ...
```

`empty_drive_trash` should additionally require the count of items currently in trash to be passed as `expected_count` (fail fast if the actual count differs). This prevents an agent from emptying trash that grew unexpectedly between the search and the call.

### Idempotence + dry-run

`trash_drive_file` should be idempotent (already-trashed → no-op return). `delete_drive_file_permanent` on an already-deleted file should return a structured "not found" not a raw 404. Both destructive tools should support a `dry_run: bool` mode that returns the file metadata they *would* delete, so an agent can show the user the plan before committing.

### Audit trail

Drive doesn't return rich audit data on `files.delete()` — just success/failure. Consider logging each destructive call to a session-local JSONL (path, file_id, mime_type, size, parents, sha — all fetched pre-delete) so a misuse can be reconstructed even though the file itself is gone. Out-of-scope for v1 if it bloats the change.

## Open questions

- Should `empty_drive_trash` accept a `query` filter to only purge matching items? (Drive API natively supports `q=` only on `files.list`, not `files.emptyTrash` — we'd have to list-and-loop, which loses atomicity.)
- Tool surface for shared drives: `files.delete` on a shared drive item requires `supportsAllDrives=true` and a different permission model. Initial implementation can scope to My Drive only, with explicit "shared drive support TBD" in tool descriptions.
- Should we add a top-level `mcp__workspace-mm__list_drive_trash` shortcut, or rely on `search_drive_files(q="trashed=true")`? The dedicated tool is more discoverable; the search query already works. Slight DRY violation either way.
- Hard-fail vs partial success for `empty_drive_trash`: Drive returns success only if all items deleted. If one item is locked (someone else's permission, etc.), the whole call fails. Surface this in the tool description.

## Cross-references

- Triggering session: age-vault implementation, May 2026 — discovered when Drive Trash retained plaintext credentials after `rm -rf` of repo subtree.
- Related: `mcp__gmail-mm__delete_email` already follows the trash-vs-permanent split (uses `gmail.modify` for soft, `mail.google.com` for hard). Same idiom should apply here.
- Upstream: `taylorwilsdon/google_workspace_mcp` (the parent of the AeyeOps fork) — worth checking whether they've already shipped this and we can pull rather than implement.
