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

Full codicon list: https://microsoft.github.io/vscode-codicons/dist/codicon.html

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
them. This pattern was validated in production and the lessons below reflect real failures and their
fixes.

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

### WebviewView CSP — The Three-Stage Trap

Webview Content Security Policy failures are silent — nothing renders, no error in console.
Three separate CSP issues chain together when adding a WebviewView:

**Stage 1: Inline onclick blocked.** Default CSP blocks all inline event handlers. Symptoms:
click handlers silently do nothing — no console error unless you open webview devtools.

Fix: Use event delegation with `data-` attributes and a nonce-guarded script:

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

**Stage 2: Nonce-based style-src breaks inline styles.** If you set
`style-src 'nonce-${nonce}'`, all `style="..."` attributes on elements are blocked too —
all dynamic colors disappear silently.

The definitive fix is moving ALL dynamic colors from inline `style=""` attributes to CSS
classes. Each row gets a state class (e.g., `class="row s-idle"`, `class="row s-thinking"`),
and a static `<style nonce="${nonce}">` block defines per-state colors:

```css
.s-idle .dot { background: var(--vscode-charts-green); }
.s-idle .status { color: var(--vscode-charts-green); }
.s-idle { border-left-color: var(--vscode-charts-green); }
.s-thinking .dot { background: var(--vscode-charts-yellow); }
.s-thinking .status { color: var(--vscode-charts-yellow); }
/* ... per state */
```

This eliminates inline style attributes entirely, so style-src only needs to allow the nonce
for the `<style>` block. If you still need `'unsafe-inline'` for style-src (e.g., for VS Code
theme variable usage), it is safe because styles cannot execute code.

**Stage 3: Missing webview.cspSource.** Without `${webview.cspSource}` in style-src, external
CSS loaded via `<link>` tags and VS Code's own injected styles fail to load.

**Final working CSP pattern:**

```typescript
`<meta http-equiv="Content-Security-Policy" content="
  default-src 'none';
  style-src ${webview.cspSource} 'unsafe-inline';
  script-src 'nonce-${nonce}';
  img-src ${webview.cspSource} https:;
  font-src ${webview.cspSource};
">`
```

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

If you cache ownership or mapping data (e.g., which items belong to this VS Code window),
**never clear the entire cache** — it makes all items fail ownership checks, causing the panel
to go blank until the next async detection cycle completes.

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

terminal.show();                    // focus this terminal
terminal.sendText('echo hello');    // execute a command
terminal.sendText('exit', true);    // send text + Enter

// Get process info
const pid = await terminal.processId;
```

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
// For files outside workspace folders, use an absolute glob
const watcher = vscode.workspace.createFileSystemWatcher(
  new vscode.RelativePattern(
    vscode.Uri.file('/home/user/.config/myapp'),
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
