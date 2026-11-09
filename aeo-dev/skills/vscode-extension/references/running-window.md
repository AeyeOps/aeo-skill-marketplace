# Driving an Open VS Code Window from a Shell

How a script or an agent runs a VS Code command in a window that is already open, such as
reloading it after an extension update, without the window having keyboard focus. Verified on
Linux desktop VS Code 1.144 and Insiders 1.145, where each window's extension host is an Electron
utility process.

## Why the usual routes fail

- The `code` CLI opens files, folders, diffs and chat sessions and manages extensions, but has
  no option that runs a command in a window.
- VS Code takes keystrokes only while its window has keyboard focus. A Wayland compositor can
  deliver keys to a window in the background, and a terminal there receives them, but VS Code
  drops them.
- A `vscode://` URL reaches only an extension's own URI handler, and opening one raises the
  window.

## The route that works

VS Code starts each window's extension host with `--inspect-port=0`. Sending that process
`SIGUSR1` opens its Node inspector on a free port on `127.0.0.1`, and an inspector session can
call the `vscode` API inside that window. The skill's `scripts/vscode-command.mjs` does this end
to end:

```bash
node <skill folder>/scripts/vscode-command.mjs <workspace folder> <command id> [JSON argument ...]
```

It needs Node 22 or later, for the built-in `WebSocket`. It:

1. finds every `code` or `code-insiders` process whose command line holds
   `--utility-sub-type=node.mojom.NodeService` and `--inspect-port=0`, reading
   `/proc/<pid>/cmdline` split on NUL or space, because Chromium rewrites its command line as one
   space-joined string;
2. sends each one `SIGUSR1`, finds its inspector port with `ss -ltnp`, and asks it for
   `workspace.workspaceFolders`;
3. runs `commands.executeCommand(<command id>, ...arguments)` in the window whose folder
   matches, waiting up to 10 seconds for the result;
4. closes each inspector it opened with `inspector.close()`, after its own session ends, and
   waits until the port is gone, so a second run does not race the first one's close.

It prints one JSON line: the folder, the command, the extension host's pid, whether that host
exited, and the command's `value`, `exception`, or `pending` state. Exit codes: 0 when the
command ran or the host exited, 1 when no window has the folder open (the error lists the
folders it found), 2 for a usage error, 3 when the command threw and the host is still running.

Inside the inspector the API comes from
`require('node:module').createRequire(process.execPath)('vscode')`. The host cannot tie that
caller to an extension, so it serves its default API and logs a warning in the window's
`exthost.log` that lists every extension folder it loaded, version included.

## Reload a window after an extension update

A first install activates in open windows at once. An update does not: each window keeps the
version it loaded until it reloads. After `code --install-extension <file>.vsix`:

```bash
node <skill folder>/scripts/vscode-command.mjs <workspace folder> workbench.action.reloadWindow
```

The output shows `extensionHostExited: true` with the exception `Canceled`, because the reload
cancels the pending command as the old host shuts down. Terminals reattach after the reload, and
the window does not raise itself or take focus from the window the user is working in.

Check which version the window runs in `~/.config/Code/logs/<session>/window<n>/exthost/exthost.log`
(`~/.config/Code - Insiders/logs/` for Insiders):

- a reload adds an `Extension host with pid <pid> started` line and a new
  `ExtensionService#_doActivateExtension <publisher>.<name>` line;
- the latest `<publisher>.<name>-<version> -> <publisher>.<name>` line, from the warning above,
  names the version the window runs.

## Limits

- Linux only as written: process discovery reads `/proc` and uses `ss`. macOS would need `ps`
  and `lsof` instead and is untested. Windows has no `SIGUSR1`.
- The inspector accepts any local process while it is open, which is why the script closes it.
- A command that opens a dialog or quick pick waits on the user and comes back `pending`.
