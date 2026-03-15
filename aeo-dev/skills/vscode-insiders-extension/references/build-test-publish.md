# Build, Test, and Publish

Complete reference for the extension build pipeline, testing infrastructure, and marketplace
publishing workflow. Supplements the main SKILL.md.

## Table of Contents

- [esbuild Configuration](#esbuild-configuration)
- [TypeScript Configuration](#typescript-configuration)
- [Testing Infrastructure](#testing-infrastructure)
- [Debugging Tests](#debugging-tests)
- [CI Setup](#ci-setup)
- [Publishing to Marketplace](#publishing-to-marketplace)
- [Platform-Specific Builds](#platform-specific-builds)
- [Pre-Release Strategy](#pre-release-strategy)
- [Marketplace Metadata](#marketplace-metadata)

---

## esbuild Configuration

The complete `esbuild.js` script, npm scripts, and `.vscodeignore` are in the main SKILL.md.
This section covers the design rationale and additional options.

### Key Configuration Decisions

- `external: ['vscode']` — the `vscode` module is provided by the runtime, never bundled
- `format: 'cjs'` — VS Code's extension host uses CommonJS
- `platform: 'node'` — extensions run in Node.js, not the browser
- `sourcemap: !production` — maps for development, omitted for published .vsix
- esbuild processes TypeScript directly but does not type-check; run `tsc --noEmit` separately

### Additional npm Scripts

Beyond the scripts in SKILL.md, consider adding:

- `"lint": "eslint src/"` — lint before publish

Install `npm-run-all` as a dev dependency for the parallel `watch` task.

### Additional .vscodeignore Entries

Beyond the entries in SKILL.md, also exclude:

- `.eslintrc*` — linter config not needed at runtime
- `**/*.map` — source maps excluded from published .vsix

---

## TypeScript Configuration

### tsconfig.json

```json
{
  "compilerOptions": {
    "module": "Node16",
    "target": "ES2022",
    "lib": ["ES2022"],
    "outDir": "out",
    "rootDir": "src",
    "sourceMap": true,
    "strict": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "out"]
}
```

The `outDir` is set to `out/` for tsc output, but esbuild writes to `dist/`. The `out/` directory
is only used for type checking and test compilation; the actual extension runs from `dist/`.

---

## Testing Infrastructure

### Setup

```bash
npm install --save-dev @vscode/test-cli @vscode/test-electron
```

### Configuration (.vscode-test.mjs)

```javascript
import { defineConfig } from '@vscode/test-cli';

export default defineConfig({
  files: 'out/test/**/*.test.js',
  version: 'stable',                    // or 'insiders'
  workspaceFolder: './test-workspace',   // optional test workspace
  mocha: {
    ui: 'tdd',
    timeout: 20000
  }
});
```

Multi-configuration example (separate unit and integration tests):

```javascript
import { defineConfig } from '@vscode/test-cli';

export default defineConfig([
  {
    label: 'unit',
    files: 'out/test/unit/**/*.test.js',
    mocha: { ui: 'tdd', timeout: 10000 }
  },
  {
    label: 'integration',
    files: 'out/test/integration/**/*.test.js',
    workspaceFolder: './test-fixtures',
    mocha: { ui: 'tdd', timeout: 30000 }
  }
]);
```

Run specific configs: `npx vscode-test --label unit`

### Writing Tests

Tests run under Mocha inside an Extension Development Host with full VS Code API access:

```typescript
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
  suiteTeardown(() => {
    vscode.window.showInformationMessage('All tests done!');
  });

  test('Command is registered', async () => {
    const commands = await vscode.commands.getCommands(true);
    assert.ok(commands.includes('myExt.doSomething'));
  });

  test('TreeView has items', async () => {
    // Trigger activation
    await vscode.commands.executeCommand('myExt.refresh');

    // Give the provider time to populate
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Assert via the extension's exported API or view state
  });

  test('Configuration defaults', () => {
    const config = vscode.workspace.getConfiguration('myExt');
    assert.strictEqual(config.get('refreshInterval'), 3000);
  });
});
```

### Test File Organization

```
src/
  test/
    unit/
      provider.test.ts    # test pure logic (no VS Code API needed)
    integration/
      extension.test.ts   # test with VS Code API
      views.test.ts
test-fixtures/             # workspace files for integration tests
  .vscode/
    settings.json
  sample-file.json
```

---

## Debugging Tests

### Launch Configuration (.vscode/launch.json)

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Extension",
      "type": "extensionHost",
      "request": "launch",
      "args": ["--extensionDevelopmentPath=${workspaceFolder}"],
      "outFiles": ["${workspaceFolder}/dist/**/*.js"],
      "preLaunchTask": "npm: compile"
    },
    {
      "name": "Extension Tests",
      "type": "extensionHost",
      "request": "launch",
      "args": [
        "--disable-extensions",
        "--extensionDevelopmentPath=${workspaceFolder}",
        "--extensionTestsPath=${workspaceFolder}/out/test/suite/index"
      ],
      "outFiles": ["${workspaceFolder}/out/test/**/*.js"],
      "preLaunchTask": "npm: compile"
    }
  ]
}
```

The `--disable-extensions` flag prevents other installed extensions from interfering with tests.

### Tasks Configuration (.vscode/tasks.json)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "type": "npm",
      "script": "watch",
      "isBackground": true,
      "problemMatcher": ["$esbuild-watch", "$tsc-watch"],
      "group": { "kind": "build", "isDefault": true }
    },
    {
      "type": "npm",
      "script": "compile",
      "problemMatcher": ["$esbuild", "$tsc"]
    }
  ]
}
```

---

## CI Setup

### GitHub Actions

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run check-types
      - run: npm run lint
      - run: xvfb-run -a npm test   # VS Code needs a display on Linux
```

The `xvfb-run` wrapper provides a virtual display for the Extension Development Host.

---

## Publishing to Marketplace

### One-Time Setup

1. Create a publisher at https://marketplace.visualstudio.com/manage
2. Create a Personal Access Token (PAT) at Azure DevOps:
   - Organization: "All accessible organizations"
   - Scopes: Marketplace → Manage
3. Login: `vsce login <publisher-id>`

### Publishing Commands

```bash
npm install -g @vscode/vsce

vsce package                         # create .vsix without publishing
vsce publish                         # publish using saved PAT
vsce publish minor                   # auto-increment minor version + publish
vsce publish 1.2.0                   # publish specific version
```

Local installation for testing:

```bash
code-insiders --install-extension my-extension-0.1.0.vsix
```

**WSL profile caveat**: If VS Code profiles are active, the CLI registers the extension in the
global registry but NOT the active profile. The extension won't load until manually added to
`~/.vscode-server-insiders/data/User/profiles/<profile-id>/extensions.json`. See the main
SKILL.md WSL Platform Notes for details.

### Pre-Publish Checklist

1. Version bumped in `package.json`
2. `CHANGELOG.md` updated
3. `README.md` describes the extension (renders as marketplace page)
4. `vscode:prepublish` script runs successfully
5. `engines.vscode` matches minimum supported version
6. `.vscodeignore` excludes dev files

---

## Platform-Specific Builds

For extensions with native dependencies:

```bash
# Package for specific platforms
vsce package --target linux-x64
vsce package --target linux-arm64
vsce package --target darwin-x64
vsce package --target darwin-arm64
vsce package --target win32-x64

# Publish multiple platforms at once
vsce publish --target linux-x64 linux-arm64 darwin-x64 darwin-arm64 win32-x64
```

Available targets: `win32-x64`, `win32-arm64`, `linux-x64`, `linux-arm64`, `linux-armhf`,
`alpine-x64`, `alpine-arm64`, `darwin-x64`, `darwin-arm64`, `web`.

For pure TypeScript extensions without native modules, platform-specific builds are unnecessary —
a single universal package works everywhere.

---

## Pre-Release Strategy

VS Code supports pre-release channels for extensions:

```bash
vsce publish --pre-release
```

Recommended version numbering:
- Release versions: `major.EVEN.patch` (e.g., `0.2.0`, `0.4.1`)
- Pre-release versions: `major.ODD.patch` (e.g., `0.3.0`, `0.5.0`)

Users opt into pre-release via the marketplace or Extensions view. VS Code auto-updates to
the highest available version, so pre-release users may receive stable updates if the stable
version number is higher.

---

## Marketplace Metadata

### package.json Fields

```json
{
  "publisher": "my-publisher-id",
  "displayName": "My Extension",
  "description": "One-line description for search results",
  "version": "0.1.0",
  "icon": "media/icon.png",
  "categories": ["Other"],
  "keywords": ["keyword1", "keyword2"],
  "pricing": "Free",
  "repository": {
    "type": "git",
    "url": "https://github.com/user/repo"
  },
  "sponsor": {
    "url": "https://github.com/sponsors/user"
  },
  "galleryBanner": {
    "color": "#1e1e1e",
    "theme": "dark"
  }
}
```

### Categories

Valid marketplace categories: `Azure`, `Data Science`, `Debuggers`, `Education`,
`Extension Packs`, `Formatters`, `Keymaps`, `Language Packs`, `Linters`, `Machine Learning`,
`Notebooks`, `Other`, `Programming Languages`, `SCM Providers`, `Snippets`, `Testing`,
`Themes`, `Visualization`.

### Keywords

Maximum 30 keywords. These improve discoverability in marketplace search.

### Icon

- Format: PNG, 128x128px minimum, 256x256px recommended
- Must be in the extension package (local file, not URL)

### Badges

```json
{
  "badges": [
    {
      "url": "https://img.shields.io/badge/...",
      "href": "https://...",
      "description": "Build Status"
    }
  ]
}
```

Only badges from approved services (shields.io, travis-ci.org, etc.) are allowed.

### Extension Packs

Bundle multiple extensions together:

```json
{
  "extensionPack": [
    "publisher.extension1",
    "publisher.extension2"
  ]
}
```

### Extension Dependencies

Declare extensions that must be installed:

```json
{
  "extensionDependencies": [
    "publisher.required-extension"
  ]
}
```
