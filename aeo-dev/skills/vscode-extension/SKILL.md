---
name: vscode-extension
description: |
  Use when building, debugging, testing or publishing a VS Code extension, on stable VS Code or Insiders
  (code-insiders), on Windows, macOS or Linux desktop or in a WSL or SSH remote: scaffolding and bundling with
  esbuild, TreeView and WebviewView panels, blank webviews from Content Security Policy violations, terminal
  commands through shell integration, language model tools, chat participants and MCP server providers,
  extensions that do not load after install under profiles, getting an updated extension into windows that
  are already open, and running VS Code commands in an open window from a shell or script. Not for VS Code
  user configuration such as themes, keybindings or tasks.json, browser extensions, Electron apps, JupyterLab
  plugins, or Monaco Editor embeds.
license: MIT
metadata:
  author: AeyeOps
  version: "0.4.0"
  summary: Verified workflows for building, testing, publishing and driving VS Code extensions on stable VS Code and Insiders.
---

# VS Code Extension Development

Guide for building VS Code extensions from scaffold through publication, and for driving the
windows that run them.

When VS Code's behavior in a session contradicts a line here, or a VS Code release changes it,
tell the user which line is wrong and what you observed, and correct the line in the skill's
source when you have it. The vendor pages this skill was checked against are listed in
[references/provenance.md](references/provenance.md); read it when a fact here needs re-checking.

## Environment Notes

VS Code extensions run in three environments, on either stable VS Code or Insiders. The extension
code and APIs are identical everywhere; what differs is where files live and how the extension
host starts.

### Stable and Insiders

Insiders is a separate install with its own CLI, folders and settings, and runs about one weekly
release ahead of stable. When the user develops on Insiders, every command, launch configuration
and documentation reference in their project uses `code-insiders`. The sections below name
stable's paths; Insiders uses these instead:

| | Stable | Insiders |
|---|---|---|
| CLI | `code` | `code-insiders` |
| Extensions | `~/.vscode/extensions/` | `~/.vscode-insiders/extensions/` |
| User data, Linux | `~/.config/Code/User/` | `~/.config/Code - Insiders/User/` |
| User data, macOS | `~/Library/Application Support/Code/User/` | `~/Library/Application Support/Code - Insiders/User/` |
| User data, Windows | `%APPDATA%\Code\User\` | `%APPDATA%\Code - Insiders\User\` |
| Logs, Linux | `~/.config/Code/logs/` | `~/.config/Code - Insiders/logs/` |
| Remote server, WSL or SSH | `~/.vscode-server/` | `~/.vscode-server-insiders/` |

On Windows the extensions folders are `%USERPROFILE%\.vscode\extensions\` and
`%USERPROFILE%\.vscode-insiders\extensions\`.

### Native (Windows/macOS/Linux desktop)

The extension host runs locally on the same machine as the VS Code UI.

- **CLI**: `code`
- **Extensions**: `%USERPROFILE%\.vscode\extensions\` (Windows), `~/.vscode/extensions/` (macOS/Linux)
- **User data**: `%APPDATA%\Code\User\` (Windows), `~/Library/Application Support/Code/User/` (macOS), `~/.config/Code/User/` (Linux)
- **Profile settings**: `<user-data>/profiles/<profile-id>/settings.json`
- **Profile extensions**: `<user-data>/profiles/<profile-id>/extensions.json`
- **File watchers**: OS-native (ReadDirectoryChangesW on Windows, FSEvents on macOS, inotify on Linux)
- **Install**: `code --install-extension my-ext.vsix`
- **`process.env`**: The desktop extension host lacks terminal variables such as
  `VSCODE_IPC_HOOK_CLI`; read them from a terminal's `/proc/<terminal_pid>/environ`

### WSL Remote (VS Code on Windows, extension host in WSL)

VS Code runs on Windows but connects to a WSL distro. The extension host runs inside WSL as a
Node.js server. Extensions split across two locations — UI extensions (themes, keymaps) stay on
Windows, workspace extensions run in WSL.

- **CLI**: `code` (available inside WSL via the VS Code Server shim)
- **Server-side extensions (WSL)**: `~/.vscode-server/extensions/`
- **UI-side extensions (Windows)**: `%USERPROFILE%\.vscode\extensions\`
  (from WSL: `"$(wslpath "$(cmd.exe /c 'echo %USERPROFILE%' | tr -d '\r')")/.vscode/extensions/"`)
- **Server-side profiles (WSL)**: `~/.vscode-server/data/User/profiles/<profile-id>/extensions.json`
- **Settings/keybindings (Windows)**: `%APPDATA%\Code\User\profiles\<profile-id>\settings.json`
  (from WSL: `"$(wslpath "$(cmd.exe /c 'echo %APPDATA%' | tr -d '\r')")/Code/User/profiles/<profile-id>/"`)
  — the Windows side is **authoritative** for UI/editor settings (theme, font, keybindings,
  layout). The WSL server-side profile at `~/.vscode-server/data/User/profiles/<profile-id>/`
  has only a minimal `settings.json` — most settings are not duplicated there.
  Workspace-level overrides go in `.vscode/settings.json` in the project dir on WSL.
- **File watchers**: inotify-backed via VS Code's API — always prefer `createFileSystemWatcher()`
  over Node.js `fs.watch()` which has cross-platform inconsistencies
- **Path translation**: Not needed for extension code — the extension host runs natively in WSL.
  Windows paths are only relevant for the VS Code UI process.
- **Install**: `code --install-extension my-ext.vsix` (runs inside WSL, installs to WSL server dir)
- **`process.env`**: The remote extension host sets `VSCODE_IPC_HOOK_CLI` to its own CLI socket,
  so a `code` command the extension spawns reaches its window

### SSH Remote (VS Code on any OS, extension host on remote Linux)

Same architecture as WSL Remote — extensions install to `~/.vscode-server/` on the remote host,
the extension host runs as a Node.js server over SSH. Same constraints as WSL Remote apply.

### Launch Config

Use `${execPath}` in `.vscode/launch.json` — it resolves correctly in all three environments and
on both builds.

## Quick Start — Scaffold a New Extension

Generate a TypeScript extension project:

```bash
npx --package yo --package generator-code -- yo code
```

Select "New Extension (TypeScript)" when prompted, and choose esbuild at "Which bundler to use?"
(or pass `--bundler=esbuild`); the default is unbundled. This creates a ready-to-run project with
`src/extension.ts`, `package.json`, `esbuild.js`, TypeScript and ESLint configuration, and tests.

Open the project and launch the Extension Development Host with F5 to test immediately.

## Project Structure

```
extension-name/
  package.json            # manifest: contribution points, activation, settings
  esbuild.js              # build script
  tsconfig.json           # TypeScript config
  eslint.config.mjs       # ESLint flat config
  .vscodeignore           # files excluded from .vsix package
  .vscode-test.mjs        # test runner configuration
  src/
    extension.ts          # activate() / deactivate() entry point
    *.ts                  # feature modules
    test/                 # tests, compiled to out/ by compile-tests
  dist/
    extension.js          # bundled output (single file)
```

Keep `src/` organized by feature. Each major capability (a TreeView provider, a webview, a
command group) gets its own module file. The `extension.ts` entry point wires them together
in `activate()` and tears them down in `deactivate()`.

## package.json — The Extension Manifest

The manifest declares everything the extension contributes to VS Code. Key fields:

```jsonc
{
  "name": "my-extension",
  "displayName": "My Extension",
  "version": "0.1.0",
  "engines": { "vscode": "^1.110.0" },   // minimum VS Code; caret = forward-compatible
  "main": "./dist/extension",             // points to esbuild output
  "activationEvents": [],                 // usually auto-inferred
  "contributes": { /* see below */ }
}
```

### Activation Events

VS Code auto-generates activation events for most contribution points — you rarely need to
declare them manually. Notable exceptions:

- `onWebviewPanel:viewType` — for webview panel restoration
- `onUri` — for URI handlers
- `onStartupFinished` — activate after VS Code has started, without delaying startup
- `*` — activate during startup; use `onStartupFinished` unless the extension must be ready first

For views (`contributes.views`), VS Code automatically activates on `onView:viewId`.

### Contribution Points

The `contributes` object declares UI elements, commands, settings, and more:

```jsonc
{
  "contributes": {
    // Commands the extension provides
    "commands": [{
      "command": "myExt.refresh",
      "title": "Refresh",
      "icon": "$(refresh)",              // codicon reference
      "category": "My Extension"
    }],

    // Views in the sidebar, panel, or built-in containers
    "views": {
      "explorer": [{                     // built-in container
        "id": "myView",
        "name": "My View"
      }]
    },

    // Custom view containers (activity bar or panel)
    "viewsContainers": {
      "activitybar": [{
        "id": "myContainer",
        "title": "My Container",
        "icon": "media/icon.svg"
      }],
      "panel": [{
        "id": "myPanel",
        "title": "My Panel",
        "icon": "media/icon.svg"
      }]
    },

    // Toolbar and context menu placement
    "menus": {
      "view/title": [{                   // toolbar at top of view
        "command": "myExt.refresh",
        "when": "view == myView",
        "group": "navigation"            // shows as icon, not menu item
      }],
      "view/item/context": [{            // right-click on tree items
        "command": "myExt.openItem",
        "when": "view == myView && viewItem == editable",
        "group": "inline"                // inline icon on the row
      }]
    },

    // Welcome content for empty views
    "viewsWelcome": [{
      "view": "myView",
      "contents": "No items found.\n[Get Started](command:myExt.init)"
    }],

    // User-configurable settings
    "configuration": {
      "title": "My Extension",
      "properties": {
        "myExt.refreshInterval": {
          "type": "number",
          "default": 3000,
          "description": "Refresh interval in milliseconds"
        }
      }
    }
  }
}
```

### Menu `when` Clauses

Control visibility with boolean expressions:
- `view == myView` — only in a specific view
- `viewItem == someContext` — only for tree items with that `contextValue`
- `resourceScheme == file` — only for file URIs
- Combine with `&&`, `||`, `!`

### Menu Group Ordering

Use `@` suffix for ordering within a group: `"navigation@1"`, `"navigation@2"`.

## Extension Entry Point

```typescript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  // Register commands, providers, watchers here
  // Push disposables to context.subscriptions for cleanup

  const disposable = vscode.commands.registerCommand('myExt.hello', () => {
    vscode.window.showInformationMessage('Hello!');
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {
  // Cleanup if needed (most things auto-dispose via subscriptions)
}
```

Every disposable (commands, watchers, providers, views) should be pushed to
`context.subscriptions` so VS Code cleans them up on deactivation.

## Core API Patterns

This section covers the most common patterns. When implementing TreeView, Webview, WebviewView,
Terminal, FileSystemWatcher, StatusBar, command or configuration code, read
[references/api-patterns.md](references/api-patterns.md) for full examples.

### TreeView

The most common way to add structured data to the sidebar or panel:

1. Implement `TreeDataProvider<T>` with `getChildren()` and `getTreeItem()`
2. Fire `onDidChangeTreeData` to refresh
3. Register via `vscode.window.createTreeView()` for full API access

TreeItems support labels, descriptions, tooltips, icons (ThemeIcon or custom SVG), collapsible
state, contextValue (for menu filtering), and a command to execute on click.

### Webview

For custom HTML/CSS/JS interfaces when TreeView isn't sufficient:

1. Create with `vscode.window.createWebviewPanel()` or implement `WebviewViewProvider`
2. Set HTML content, load local resources via `webview.asWebviewUri()`
3. Communicate via `postMessage()` / `onDidReceiveMessage()`
4. Always set a Content Security Policy

Webviews are sandboxed — they cannot access the filesystem directly. All communication goes
through the message passing API.

### Dual View: TreeView + WebviewView Toggle

When you need richer presentation than TreeView allows (multi-line rows, colored status text,
custom layouts), add a WebviewView alongside the existing TreeView with a toolbar toggle. The
pattern involves:

1. Register both views in the same `viewsContainers` entry with `when` clauses on a context key
2. Toggle commands flip the context key and persist to `globalState`
3. Both providers share a single data pipeline and refresh together
4. User interactions in both views route through shared VS Code commands (not direct calls)
5. CSP: a nonce for scripts, `${webview.cspSource}` for the extension's stylesheet, and dynamic
   styling through CSS classes rather than inline `style` attributes

This pattern has several non-obvious failure modes (silent CSP blocking, cache invalidation
blanking the panel, stale focus handlers). Before building it, read the Dual View section of
[references/api-patterns.md](references/api-patterns.md).

### Terminal

For interacting with VS Code's integrated terminal:

- `window.createTerminal()` — create terminals
- `terminal.sendText(text)` — type the text and press Enter; pass `false` as the second argument
  to leave it unexecuted
- `terminal.shellIntegration.executeCommand()` — run a command and get its exit code from
  `onDidEndTerminalShellExecution` and its output from `execution.read()`; shell integration can
  arrive after the terminal opens, so the Terminal section of
  [references/api-patterns.md](references/api-patterns.md) waits for it and falls back to `sendText`
- `terminal.show()` — focus a terminal (handles tabs and split panes)
- `terminal.processId` — get the underlying PID
- `window.terminals` — enumerate all open terminals
- `onDidOpenTerminal` / `onDidCloseTerminal` — lifecycle events

### Chat, Language Model Tools and MCP

An extension can give the chat agent a tool (`vscode.lm.registerTool` with
`contributes.languageModelTools`), add an `@`-participant to the chat view
(`vscode.chat.createChatParticipant` with `contributes.chatParticipants`), and offer MCP servers
(`vscode.lm.registerMcpServerDefinitionProvider` with `contributes.mcpServerDefinitionProviders`).
VS Code generates the activation event for each from its contribution. When building one, read the
Chat, Language Model Tools and MCP section of
[references/api-patterns.md](references/api-patterns.md).

### FileSystemWatcher

For reacting to file changes on disk. Prefer the VS Code API over Node.js `fs.watch()` because
it runs outside the editor process and uses efficient OS-level notifications (inotify on Linux):

```typescript
const watcher = vscode.workspace.createFileSystemWatcher(
  new vscode.RelativePattern(folder, '**/*.json')
);
watcher.onDidChange(uri => { /* file modified */ });
watcher.onDidCreate(uri => { /* file created */ });
watcher.onDidDelete(uri => { /* file deleted */ });
context.subscriptions.push(watcher);
```

### StatusBar

- `window.createStatusBarItem(alignment, priority)` — left or right alignment
- Convention: left side = workspace-scoped info, right side = file-scoped info
- Set `text`, `tooltip`, `command`, `color`, `backgroundColor`

## Building with esbuild

esbuild bundles `src/extension.ts` into a single `dist/extension.js`. The `vscode` module stays
external because the extension host provides it, and `tsc --noEmit` type-checks separately because
esbuild strips types without checking them. `vscode:prepublish` runs automatically during
`vsce package` and `vsce publish`.

When setting up or changing the build, read
[references/build-test-publish.md](references/build-test-publish.md) for the complete `esbuild.js`,
the npm scripts and `.vscodeignore`.

## Testing

For test configuration, debugging tests and CI, read
[references/build-test-publish.md](references/build-test-publish.md).

Tests run under Mocha inside an Extension Development Host with full VS Code API access.
`@vscode/test-cli` reads `.vscode-test.mjs`, whose `files` glob points at compiled tests in `out/`.
esbuild writes only `dist/`, so a `compile-tests` script must compile the tests to `out/`, and a
`pretest` script runs it before `npm test`; without them the run finds no tests and still passes.

## Publishing

For publisher setup, pre-release versions, platform targets and marketplace metadata, read
[references/build-test-publish.md](references/build-test-publish.md).

Quick reference:

```bash
npm install -g @vscode/vsce
vsce package                      # creates .vsix
vsce publish                      # publishes to marketplace
vsce publish minor                # auto-increment + publish
vsce publish --pre-release        # pre-release channel
code --install-extension my-ext-0.1.0.vsix   # local install
```

`vsce publish` from CI authenticates through a federated identity (`--oidc` on GitHub Actions,
`--azure-credential` on Azure Pipelines); global Azure DevOps tokens retire on December 1, 2026.
Platform-specific packages take one `vsce package --target <target>` per target.

### Updating an Extension in Open Windows

A first install activates in every open window at once. An update does not: each window keeps
running the version it loaded until it reloads, so a window that has not reloaded still shows the
old behavior. After installing an updated `.vsix`, reload each open window that uses it before
judging the new version. In a local window, the Restart Extensions button VS Code offers after an
update applies it without a full reload; a WSL or SSH window needs Reload Window. That button has
no command id, and Developer: Restart Extension Host only stops and restarts the hosts, so a script
uses Reload Window.

A shell cannot press Reload Window in a window that lacks keyboard focus, and the `code` CLI has
no option that runs a command. When a script or agent must reload a window, or run any other
command in it, read [references/running-window.md](references/running-window.md) and use
[scripts/vscode-command.mjs](scripts/vscode-command.mjs), which runs a command in the window
that has a given folder open.

### Stable vs Insiders — Same Extension

A `.vsix` package works on both VS Code stable and Insiders — there is no separate build. The
only factor is the `engines.vscode` version in `package.json`:

- `"^1.110.0"` means the extension requires VS Code 1.110+. If a new API you use only exists
  in Insiders, stable users can't install until that version ships. Use the lowest version that
  supports the APIs you need.
- When developing on Insiders, test against stable before publishing for broad reach.
- Pin `@types/vscode` to the same floor. The generator writes the newest version to both, and
  `vsce package` refuses a package whose `@types/vscode` is newer than `engines.vscode`.
- The marketplace serves the same package to both builds.

## Platform Notes

### Profile-Based Extension Registration

`code --install-extension` installs into the default profile unless told otherwise, so an
extension installed while a window uses another profile does not load there.

- On desktop, `--profile <name>` installs into that profile, matched by name. An unknown name
  fails with `Profile '<name>' not found.`
- From a plain WSL or SSH shell, `--profile` is not passed on to the VS Code server, and the
  install lands in the server's default profile. Install from the window's integrated terminal
  instead, which installs into the window's current profile, or add the extension to
  `~/.vscode-server/data/User/profiles/<profile-id>/extensions.json` by hand.
- Without a `publisher` field in package.json, the extension installs as
  `undefined_publisher.<name>-<version>`.

Each profile's extension list is `<user-data>/profiles/<profile-id>/extensions.json` on desktop.

### Webview Content Security Policy

- Violations are silent; Developer: Open Webview Developer Tools shows them
- Inline `onclick` attributes are blocked — use a nonce-guarded `<script>` with
  `addEventListener` instead
- Inline `style=""` attributes are blocked unless `style-src` allows `'unsafe-inline'`, and a
  nonce in the same directive cancels `'unsafe-inline'` — move dynamic styling to CSS classes
- Include `${webview.cspSource}` in `style-src` so the extension's stylesheet loads
- Theme variables such as `--vscode-editor-foreground` need no CSP allowance

### Architecture Constraints

- Extensions run in the extension host, separate from the VS Code UI. On desktop each window has
  its own host, an Electron utility process started with `--inspect-port=0`; in a WSL or SSH
  window the host runs as a Node.js server on the remote
- The Node extension host loads `main` as ESM when the file ends in `.mjs`, or when
  `"type": "module"` is set and the file is not `.cjs` (VS Code 1.100 and later); CommonJS
  still works
- No DOM access — you cannot manipulate VS Code's UI directly
- No custom CSS injection — use contribution points and the API
- Webviews are sandboxed with their own security context
