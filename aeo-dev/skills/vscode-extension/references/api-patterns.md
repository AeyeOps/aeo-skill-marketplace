# VS Code Extension API Patterns

Detailed code examples for the most commonly used VS Code extension APIs. This file supplements
the main SKILL.md — read when implementing any of these patterns.

## Table of Contents

- [TreeView](#treeview)
- [Webview Panel](#webview-panel)
- [WebviewView Provider](#webviewview-provider)
- [Dual View: TreeView + WebviewView Toggle](#dual-view-treeview--webviewview-toggle)
- [Terminal API](#terminal-api)
- [FileSystemWatcher](#filesystemwatcher)
- [Status Bar](#status-bar)
- [Commands](#commands)
- [Configuration](#configuration)
- [Chat, Language Model Tools and MCP](#chat-language-model-tools-and-mcp)
- [Disposable Pattern](#disposable-pattern)

---

## TreeView

### TreeDataProvider Implementation

```typescript
import * as vscode from 'vscode';

interface MyItem {
  name: string;
  children?: MyItem[];
}

class MyTreeProvider implements vscode.TreeDataProvider<MyItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<MyItem | undefined | void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private items: MyItem[] = [];

  getTreeItem(element: MyItem): vscode.TreeItem {
    const item = new vscode.TreeItem(
      element.name,
      element.children?.length
        ? vscode.TreeItemCollapsibleState.Collapsed
        : vscode.TreeItemCollapsibleState.None
    );

    // Secondary text shown after the label
    item.description = 'some detail';

    // Hover text (string or MarkdownString)
    item.tooltip = new vscode.MarkdownString(`**${element.name}**\nMore info here`);

    // Icon — use ThemeIcon for built-in codicons, or custom SVG
    item.iconPath = new vscode.ThemeIcon('circle-filled', new vscode.ThemeColor('charts.green'));

    // Enables filtering in view/item/context menus via "viewItem == myContext"
    item.contextValue = 'myContext';

    // Command executed when user clicks this item
    item.command = {
      command: 'myExt.selectItem',
      title: 'Select',
      arguments: [element]
    };

    return item;
  }

  getChildren(element?: MyItem): MyItem[] {
    if (!element) {
      return this.items;  // root level
    }
    return element.children ?? [];
  }

  refresh(): void {
    this._onDidChangeTreeData.fire();  // undefined = refresh entire tree
  }

  refreshItem(item: MyItem): void {
    this._onDidChangeTreeData.fire(item);  // refresh specific subtree
  }
}
```

### Registration

```typescript
// Option 1: Basic — no programmatic access to the view
vscode.window.registerTreeDataProvider('myView', provider);

// Option 2: Full — returns TreeView object for programmatic operations
const treeView = vscode.window.createTreeView('myView', {
  treeDataProvider: provider,
  showCollapseAll: true,   // adds collapse-all button to toolbar
  canSelectMany: false,    // multi-select support
});

// Programmatic operations
treeView.reveal(item, { select: true, focus: true, expand: true });
treeView.title = 'Updated Title';
treeView.badge = { value: 5, tooltip: '5 items' };
treeView.message = 'Loading...';  // shown at top of view

context.subscriptions.push(treeView);
```

### ThemeIcon Reference

Common codicons for tree items: `circle-filled`, `circle-outline`, `check`, `error`, `warning`,
`info`, `file`, `folder`, `symbol-method`, `symbol-property`, `gear`, `refresh`, `play`, `debug`,
`terminal`, `eye`, `edit`, `trash`, `add`, `remove`.

ThemeColors for icons: `charts.green`, `charts.yellow`, `charts.blue`, `charts.red`,
`charts.orange`, `charts.purple`, `errorForeground`, `warningForeground`.

Full codicon list: the Codicon reference page in the vscode-codicons project.

---

## Webview Panel

### Creating a Webview Panel

```typescript
const panel = vscode.window.createWebviewPanel(
  'myPanel',                       // internal identifier
  'My Panel Title',                // displayed in tab
  vscode.ViewColumn.One,           // editor column
  {
    enableScripts: true,
    localResourceRoots: [
      vscode.Uri.joinPath(context.extensionUri, 'media')
    ],
    retainContextWhenHidden: false  // true = keep JS running when tab hidden
  }
);

// Tab icon (can use ThemeIcon as of v1.110)
panel.iconPath = new vscode.ThemeIcon('dashboard');
```

### Setting HTML Content

```typescript
function getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri): string {
  // Convert local file paths to webview-safe URIs
  const scriptUri = webview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, 'media', 'main.js')
  );
  const styleUri = webview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, 'media', 'style.css')
  );
  const nonce = getNonce();

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy"
    content="default-src 'none';
      style-src ${webview.cspSource};
      script-src 'nonce-${nonce}';
      img-src ${webview.cspSource} https:;
      font-src ${webview.cspSource};">
  <link href="${styleUri}" rel="stylesheet">
</head>
<body>
  <div id="app"></div>
  <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
}

function getNonce(): string {
  let text = '';
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for (let i = 0; i < 32; i++) {
    text += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return text;
}
```

### Message Passing

```typescript
// Extension → Webview
panel.webview.postMessage({ type: 'update', data: myData });

// Webview → Extension
panel.webview.onDidReceiveMessage(
  message => {
    switch (message.type) {
      case 'ready':
        // Webview loaded, send initial data
        break;
      case 'action':
        vscode.commands.executeCommand(message.command);
        break;
    }
  },
  undefined,
  context.subscriptions
);
```

In the webview's JavaScript:

```javascript
const vscode = acquireVsCodeApi();  // call once, reuse

// Receive from extension
window.addEventListener('message', event => {
  const message = event.data;
  if (message.type === 'update') {
    renderData(message.data);
  }
});

// Send to extension
vscode.postMessage({ type: 'action', command: 'myExt.doThing' });

// Persist lightweight state across visibility changes
vscode.setState({ scrollPosition: 42 });
const state = vscode.getState();  // { scrollPosition: 42 }
```

### Lifecycle

```typescript
// Detect visibility changes
panel.onDidChangeViewState(e => {
  if (e.webviewPanel.visible) {
    // Panel became visible — update content
  }
});

// Cleanup when panel is closed
panel.onDidDispose(() => {
  // Release resources
}, null, context.subscriptions);
```

### Serialization (restore on restart)

```typescript
// In activate():
vscode.window.registerWebviewPanelSerializer('myPanel', {
  async deserializeWebviewPanel(panel: vscode.WebviewPanel, state: any) {
    panel.webview.html = getWebviewContent(panel.webview, context.extensionUri);
    if (state) {
      panel.webview.postMessage({ type: 'restore', data: state });
    }
  }
});

// In package.json:
"activationEvents": ["onWebviewPanel:myPanel"]
```

### Theming CSS

Webviews automatically get VS Code theme CSS variables:

```css
body {
  color: var(--vscode-editor-foreground);
  background-color: var(--vscode-editor-background);
  font-family: var(--vscode-editor-font-family);
  font-size: var(--vscode-editor-font-size);
}

/* Theme-specific styles */
body.vscode-light { /* light theme overrides */ }
body.vscode-dark { /* dark theme overrides */ }
body.vscode-high-contrast { /* high contrast overrides */ }

/* Accessibility */
body.vscode-reduce-motion * { transition: none !important; }
```

---

## WebviewView Provider

For webviews embedded in the sidebar or panel (not standalone editor tabs):

```typescript
class MyWebviewViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'myExt.sidebarView';

  constructor(private readonly extensionUri: vscode.Uri) {}

  resolveWebviewView(
    webviewView: vscode.WebviewView,
    _context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this.extensionUri]
    };

    webviewView.webview.html = this.getHtml(webviewView.webview);

    webviewView.webview.onDidReceiveMessage(message => {
      // Handle messages
    });
  }

  private getHtml(webview: vscode.Webview): string {
    // Same pattern as panel webview
    return '...';
  }
}

// In activate():
context.subscriptions.push(
  vscode.window.registerWebviewViewProvider(
    MyWebviewViewProvider.viewType,
    new MyWebviewViewProvider(context.extensionUri)
  )
);
```

Register in package.json under `contributes.views` pointing to a `viewsContainers` entry.

---

## Dual View: TreeView + WebviewView Toggle

When a single TreeView isn't sufficient (e.g., you need multi-line rows, styled status text, or
custom layouts), add a WebviewView alongside the existing TreeView and let the user toggle between
them. The sections after the wiring cover the failures this pattern produces and their fixes.

### package.json — Two Views, One Container

Register both views in the same `viewsContainers` panel. Use a context key with `when` clauses
so only one is visible at a time:

```jsonc
{
  "contributes": {
    "viewsContainers": {
      "panel": [{
        "id": "myPanel",
        "title": "My Panel",
        "icon": "media/icon.svg"
      }]
    },
    "views": {
      "myPanel": [
        {
          "id": "myTreeView",
          "name": "My Data",
          "when": "myExt.viewMode != 'rich'"
        },
        {
          "id": "myRichView",
          "name": "My Data",
          "type": "webview",
          "when": "myExt.viewMode == 'rich'"
        }
      ]
    },
    "commands": [
      {
        "command": "myExt.showTreeView",
        "title": "Switch to Tree View",
        "icon": "$(list-tree)"
      },
      {
        "command": "myExt.showRichView",
        "title": "Switch to Rich View",
        "icon": "$(open-preview)"
      }
    ],
    "menus": {
      "view/title": [
        {
          "command": "myExt.showRichView",
          "when": "view == myTreeView",
          "group": "navigation"
        },
        {
          "command": "myExt.showTreeView",
          "when": "view == myRichView",
          "group": "navigation"
        }
      ]
    }
  }
}
```

The default view is the TreeView (context key is undefined or `'tree'`, which satisfies
`!= 'rich'`). The toggle button appears in the opposite view's toolbar.

### extension.ts — Registration and Toggle Wiring

```typescript
export function activate(context: vscode.ExtensionContext) {
  const treeProvider = new MyTreeProvider(/* ... */);
  const webviewProvider = new MyWebviewProvider(/* ... */);

  // Register both simultaneously — VS Code handles visibility via when-clauses
  const treeView = vscode.window.createTreeView('myTreeView', {
    treeDataProvider: treeProvider,
  });
  const webviewReg = vscode.window.registerWebviewViewProvider(
    'myRichView', webviewProvider
  );

  // Shared refresh — always update both, even the hidden one
  const bothProviders = {
    refresh() { treeProvider.refresh(); webviewProvider.refresh(); },
  };

  // Restore saved view mode — setContext is ephemeral (lost on reload),
  // so the source of truth is globalState, restored here on every activation
  const savedMode = context.globalState.get<string>('viewMode', 'tree');
  vscode.commands.executeCommand('setContext', 'myExt.viewMode', savedMode);

  // Toggle commands
  context.subscriptions.push(
    vscode.commands.registerCommand('myExt.showTreeView', () => {
      vscode.commands.executeCommand('setContext', 'myExt.viewMode', 'tree');
      context.globalState.update('viewMode', 'tree');
    }),
    vscode.commands.registerCommand('myExt.showRichView', () => {
      vscode.commands.executeCommand('setContext', 'myExt.viewMode', 'rich');
      context.globalState.update('viewMode', 'rich');
      webviewProvider.refresh(); // ensure HTML is current when view appears
    }),
    treeView,
    webviewReg,
  );
}
```

### Shared Command Routing — Critical Pattern

**Both views must route user interactions through shared VS Code commands.** Do not let the
WebviewView call provider methods directly — it creates divergent behavior.

```typescript
// WebviewView sends a message on click:
webviewView.webview.onDidReceiveMessage(message => {
  if (message.type === 'focus') {
    vscode.commands.executeCommand('myExt.focusItem', message.itemId);
  }
});

// The same command is wired as the TreeItem.command on click:
treeItem.command = {
  command: 'myExt.focusItem',
  title: 'Focus',
  arguments: [item.id]
};

// One handler serves both views:
vscode.commands.registerCommand('myExt.focusItem', async (itemId: string) => {
  // shared logic here
});
```

### WebviewView CSP — Silent Failures

Webview Content Security Policy failures are silent: nothing renders and the editor shows no
error. Open Developer: Open Webview Developer Tools to see the violations. Three of them chain
together when adding a WebviewView.

**Inline event handlers are blocked.** A CSP without `'unsafe-inline'` in `script-src` blocks
every `onclick="..."` attribute, so click handlers silently do nothing. Use event delegation with
`data-` attributes and a nonce-guarded script:

```html
<!-- Each row carries its ID as a data attribute -->
<div class="row" data-sid="${item.id}">...</div>

<script nonce="${nonce}">
  const vscode = acquireVsCodeApi();
  document.addEventListener('click', function(e) {
    const row = e.target.closest('.row');
    if (row && row.dataset.sid) {
      vscode.postMessage({ type: 'focus', itemId: row.dataset.sid });
    }
  });
</script>
```

**Inline `style=""` attributes are blocked.** A `style-src` without `'unsafe-inline'` blocks every
`style="..."` attribute, so dynamic colors disappear. Move dynamic styling to CSS classes: each row
gets a state class (`class="row s-idle"`, `class="row s-busy"`), and a stylesheet defines the
per-state colors with theme variables:

```css
.s-idle .dot { background: var(--vscode-charts-green); }
.s-idle .status { color: var(--vscode-charts-green); }
.s-busy .dot { background: var(--vscode-charts-yellow); }
.s-busy .status { color: var(--vscode-charts-yellow); }
```

Theme variables such as `--vscode-charts-green` need no CSP allowance: VS Code sets them on the
document element through script, which CSP does not restrict. Adding `'unsafe-inline'` beside a
nonce in the same directive does nothing, because a browser ignores `'unsafe-inline'` when a
nonce or hash is present.

**The stylesheet needs `${webview.cspSource}`.** A stylesheet loaded with
`<link href="${styleUri}">` from `webview.asWebviewUri()` loads only when `style-src` names
`${webview.cspSource}`.

**Working CSP**, with styles in a stylesheet and scripts behind a nonce:

```typescript
`<meta http-equiv="Content-Security-Policy" content="
  default-src 'none';
  style-src ${webview.cspSource};
  script-src 'nonce-${nonce}';
  img-src ${webview.cspSource} https:;
  font-src ${webview.cspSource};
">`
```

When the styles must stay in the page, use one `<style nonce="${nonce}">` block and add
`'nonce-${nonce}'` to `style-src`.

### Refresh Architecture for Time-Dependent Data

If your view displays computed time values (e.g., "Idle 2m 30s"), TreeView and WebviewView do
NOT auto-re-render when only derived values change. You must add a periodic refresh timer:

```typescript
const REFRESH_INTERVAL = 3000; // 3 seconds

const periodicRefresh = setInterval(() => {
  bothProviders.refresh();
}, REFRESH_INTERVAL);

context.subscriptions.push({ dispose: () => clearInterval(periodicRefresh) });
```

The WebviewView `refresh()` method should debounce to avoid excessive HTML rebuilds:

```typescript
class MyWebviewProvider implements vscode.WebviewViewProvider {
  private refreshTimer: ReturnType<typeof setTimeout> | undefined;

  refresh(): void {
    if (this.refreshTimer) clearTimeout(this.refreshTimer);
    this.refreshTimer = setTimeout(() => this.updateHtml(), 500);
  }
}
```

### Cache Invalidation on Terminal Close

If the views cache which items belong to a terminal, remove only the closed terminal's entries.
Clearing the whole cache makes every item fail its lookup, and the panel goes blank until the
next asynchronous match completes.

```typescript
// WRONG — nuclear clear, panel goes blank until matchAll() finishes
vscode.window.onDidCloseTerminal(() => {
  this.ownershipCache.clear();
});

// BETTER — clear then immediately repopulate (brief flash possible)
vscode.window.onDidCloseTerminal(() => {
  this.ownershipCache.clear();
  this.matchAll(); // synchronous repopulate
});

// BEST — remove only the closed terminal's entries, no blank flash
vscode.window.onDidCloseTerminal(closedTerminal => {
  for (const [id, terminal] of this.sessionTerminals) {
    if (terminal === closedTerminal) {
      this.sessionTerminals.delete(id);
      this.ownershipCache.delete(id);
    }
  }
  this.matchAll(); // fill in any remaining gaps
});
```

### Async Retry for Focus-on-Click

If the handler that focuses/reveals an item depends on a cache that may be stale or empty at
click time, implement on-demand re-matching before giving up:

```typescript
vscode.commands.registerCommand('myExt.focusItem', async (itemId: string) => {
  let target = this.itemCache.get(itemId);
  if (!target) {
    // Cache miss — try re-matching on demand
    await this.matchAll();
    target = this.itemCache.get(itemId);
  }
  if (target) {
    target.show(); // or reveal, focus, etc.
  }
});
```

---

## Terminal API

### Creating and Managing Terminals

```typescript
// Create a terminal
const terminal = vscode.window.createTerminal({
  name: 'My Terminal',
  cwd: '/some/directory',
  env: { MY_VAR: 'value' }
});

terminal.show();                         // focus this terminal
terminal.sendText('echo hello');         // type the text and press Enter (shouldExecute defaults to true)
terminal.sendText('partial input', false); // type without pressing Enter

// Get process info
const pid = await terminal.processId;
```

### Running a Command and Reading Its Result

`sendText` cannot tell when a command finishes or what it returned. With shell integration, which
VS Code injects into bash, zsh, fish and PowerShell, run the command through
`terminal.shellIntegration` instead:

```typescript
async function run(terminal: vscode.Terminal, commandLine: string): Promise<{ exitCode: number | undefined; output: string } | undefined> {
  const shellIntegration = terminal.shellIntegration ?? await new Promise<vscode.TerminalShellIntegration | undefined>(resolve => {
    const listener = vscode.window.onDidChangeTerminalShellIntegration(e => {
      if (e.terminal === terminal) { listener.dispose(); resolve(e.shellIntegration); }
    });
    setTimeout(() => { listener.dispose(); resolve(undefined); }, 3000);
  });
  if (!shellIntegration) {
    terminal.sendText(commandLine);   // no shell integration: no exit code or output available
    return undefined;
  }
  const execution = shellIntegration.executeCommand(commandLine);
  let output = '';
  const reading = (async () => { for await (const data of execution.read()) { output += data; } })();
  const exitCode = await new Promise<number | undefined>(resolve => {
    const listener = vscode.window.onDidEndTerminalShellExecution(e => {
      if (e.execution === execution) { listener.dispose(); resolve(e.exitCode); }
    });
  });
  await reading;
  return { exitCode, output };
}
```

Start `execution.read()` right after `executeCommand`, before awaiting the end event, or early
output is missed. The activation events `onTerminal:<shell>` and
`onTerminalShellIntegration:<shell>` activate an extension when such a terminal opens.

### Enumerating and Finding Terminals

```typescript
// All open terminals
const allTerminals = vscode.window.terminals;

// Currently focused terminal
const active = vscode.window.activeTerminal;

// Find by name
const myTerm = vscode.window.terminals.find(t => t.name === 'My Terminal');
```

### Terminal Events

```typescript
// New terminal opened
vscode.window.onDidOpenTerminal(terminal => {
  console.log(`Opened: ${terminal.name}`);
});

// Terminal closed
vscode.window.onDidCloseTerminal(terminal => {
  console.log(`Closed: ${terminal.name}, exit: ${terminal.exitStatus?.code}`);
});

// Active terminal changed
vscode.window.onDidChangeActiveTerminal(terminal => {
  console.log(`Active: ${terminal?.name}`);
});

// Shell integration became available
vscode.window.onDidChangeTerminalShellIntegration(({ terminal, shellIntegration }) => {
  // Shell integration provides command detection, cwd tracking, etc.
});
```

### Terminal.show() Behavior

`terminal.show()` handles both tab selection and split-pane focus — a single call is sufficient
to bring any terminal into view regardless of its layout position.

---

## FileSystemWatcher

### Watching Files

```typescript
// Watch specific pattern in a folder
const watcher = vscode.workspace.createFileSystemWatcher(
  new vscode.RelativePattern(someFolder, '**/*.json')
);

watcher.onDidChange(uri => {
  console.log(`Changed: ${uri.fsPath}`);
});

watcher.onDidCreate(uri => {
  console.log(`Created: ${uri.fsPath}`);
});

watcher.onDidDelete(uri => {
  console.log(`Deleted: ${uri.fsPath}`);
});

context.subscriptions.push(watcher);
```

### Watching Outside the Workspace

```typescript
// For files outside workspace folders, use an absolute base URI
// (import * as os from 'os'; import * as path from 'path';)
const watcher = vscode.workspace.createFileSystemWatcher(
  new vscode.RelativePattern(
    vscode.Uri.file(path.join(os.homedir(), '.config', 'myapp')),
    '*.json'
  )
);
```

### Why VS Code's Watcher Over Node.js fs.watch

The VS Code FileSystemWatcher runs outside the editor process and uses the OS's native file
notification system (inotify on Linux, FSEvents on macOS, ReadDirectoryChangesW on Windows).
This is more efficient and reliable than Node.js `fs.watch()`, which has known cross-platform
inconsistencies. Always prefer the VS Code API in extensions.

---

## Status Bar

```typescript
const statusBarItem = vscode.window.createStatusBarItem(
  vscode.StatusBarAlignment.Left,  // or Right
  100                               // priority (higher = further left)
);

statusBarItem.text = '$(sync~spin) Syncing...';   // codicon + text
statusBarItem.tooltip = 'Click to stop syncing';
statusBarItem.command = 'myExt.stopSync';
statusBarItem.color = new vscode.ThemeColor('statusBarItem.warningForeground');
statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
statusBarItem.show();

context.subscriptions.push(statusBarItem);
```

Animated icons: append `~spin` to a codicon name (e.g., `$(sync~spin)`) for a spinning animation.

---

## Commands

```typescript
// Register a command
const cmd = vscode.commands.registerCommand('myExt.doSomething', (arg1, arg2) => {
  // Handler receives arguments passed from menus, tree items, etc.
});

// Execute a command programmatically
await vscode.commands.executeCommand('vscode.open', uri);
await vscode.commands.executeCommand('myExt.doSomething', 'hello', 42);

// Register a text-editor-specific command (receives TextEditor and Edit)
vscode.commands.registerTextEditorCommand('myExt.format', (editor, edit) => {
  // Has access to the active editor
});
```

---

## Configuration

### Reading Settings

```typescript
const config = vscode.workspace.getConfiguration('myExt');
const interval = config.get<number>('refreshInterval', 3000);
const enabled = config.get<boolean>('enabled', true);
```

### Watching for Setting Changes

```typescript
vscode.workspace.onDidChangeConfiguration(e => {
  if (e.affectsConfiguration('myExt.refreshInterval')) {
    const newInterval = vscode.workspace.getConfiguration('myExt')
      .get<number>('refreshInterval', 3000);
    // React to the change
  }
});
```

### Updating Settings

```typescript
await vscode.workspace.getConfiguration('myExt')
  .update('refreshInterval', 5000, vscode.ConfigurationTarget.Global);
```

---

## Chat, Language Model Tools and MCP

Each of these pairs a `contributes` entry with a registration in `activate()`, and VS Code
generates the matching activation event (`onLanguageModelTool:`, `onChatParticipant:`,
`onMcpCollection:`) from the contribution.

### Language Model Tool

A tool the chat agent can call. The model reads `modelDescription` and `inputSchema` to decide when
and how:

```jsonc
"contributes": {
  "languageModelTools": [{
    "name": "myExt_findItems",
    "displayName": "Find Items",
    "toolReferenceName": "findItems",          // lets a user write #findItems in a prompt
    "canBeReferencedInPrompt": true,
    "modelDescription": "Finds items in the workspace whose name matches a query.",
    "userDescription": "Find items by name.",
    "inputSchema": {
      "type": "object",
      "properties": { "query": { "type": "string", "description": "Text to match" } },
      "required": ["query"]
    }
  }]
}
```

```typescript
interface FindItemsInput { query: string }

context.subscriptions.push(
  vscode.lm.registerTool<FindItemsInput>('myExt_findItems', {
    async invoke(options, _token) {
      const matches = await findItems(options.input.query);
      return new vscode.LanguageModelToolResult([
        new vscode.LanguageModelTextPart(JSON.stringify(matches))
      ]);
    }
  })
);
```

An optional `prepareInvocation` returns the confirmation message shown before a tool with side
effects runs. Another extension's tool is called with `vscode.lm.invokeTool(name, options)`.

### Chat Participant

An `@`-mention in the chat view with its own handler:

```jsonc
"contributes": {
  "chatParticipants": [{
    "id": "myExt.helper",
    "name": "helper",
    "fullName": "My Helper",
    "description": "Answers questions about my items"
  }]
}
```

```typescript
const participant = vscode.chat.createChatParticipant('myExt.helper',
  async (request, _context, stream, token) => {
    const [model] = await vscode.lm.selectChatModels();
    if (!model) { stream.markdown('No language model is available.'); return; }
    const response = await model.sendRequest(
      [vscode.LanguageModelChatMessage.User(request.prompt)], {}, token);
    for await (const chunk of response.text) { stream.markdown(chunk); }
  });
context.subscriptions.push(participant);
```

`request.model` holds the model the user picked in the chat view; `selectChatModels` chooses one
by vendor, family or id.

### MCP Server Definition Provider

Offers MCP servers to VS Code, which starts them and lists their tools to the chat agent:

```jsonc
"contributes": {
  "mcpServerDefinitionProviders": [{ "id": "myExt.servers", "label": "My Servers" }]
}
```

```typescript
context.subscriptions.push(
  vscode.lm.registerMcpServerDefinitionProvider('myExt.servers', {
    provideMcpServerDefinitions: async () => [
      new vscode.McpStdioServerDefinition('My Local Server', 'node', [serverScriptPath]),
      new vscode.McpHttpServerDefinition('My Remote Server', vscode.Uri.parse(serverUrl)),
    ],
  })
);
```

`resolveMcpServerDefinition` runs just before a server starts, and is the place to ask the user
for anything the server needs. Fire `onDidChangeMcpServerDefinitions` when the list changes.

---

## Disposable Pattern

Every resource that listens to events or holds references should be disposable:

```typescript
export function activate(context: vscode.ExtensionContext) {
  // Push everything to subscriptions for automatic cleanup
  context.subscriptions.push(
    vscode.commands.registerCommand('myExt.cmd', handler),
    vscode.window.createTreeView('myView', { treeDataProvider: provider }),
    vscode.workspace.createFileSystemWatcher('**/*.json'),
    statusBarItem,
    someInterval  // if you wrap setInterval: { dispose: () => clearInterval(id) }
  );
}
```

For custom disposables wrapping timers or other resources:

```typescript
function createInterval(callback: () => void, ms: number): vscode.Disposable {
  const id = setInterval(callback, ms);
  return { dispose: () => clearInterval(id) };
}
```
