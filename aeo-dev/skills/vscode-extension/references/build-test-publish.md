# Build, Test, and Publish

Reference for the extension build pipeline, tests, and marketplace publishing.

## Table of Contents

- [esbuild Configuration](#esbuild-configuration)
- [TypeScript Configuration](#typescript-configuration)
- [Testing Infrastructure](#testing-infrastructure)
- [Debugging](#debugging)
- [CI Setup](#ci-setup)
- [Publishing to Marketplace](#publishing-to-marketplace)
- [Platform-Specific Builds](#platform-specific-builds)
- [Pre-Release Strategy](#pre-release-strategy)
- [Marketplace Metadata](#marketplace-metadata)

---

## esbuild Configuration

`yo code` writes the files below when esbuild is chosen at its "Which bundler to use?" prompt, or
with `--bundler=esbuild`. They are shown here for converting an existing tsc or webpack project and
for reviewing a scaffold.

### esbuild.js

```javascript
const esbuild = require('esbuild');

const production = process.argv.includes('--production');
const watch = process.argv.includes('--watch');

/** @type {import('esbuild').Plugin} */
const esbuildProblemMatcherPlugin = {
  name: 'esbuild-problem-matcher',
  setup(build) {
    build.onStart(() => { console.log('[watch] build started'); });
    build.onEnd(result => {
      for (const { text, location } of result.errors) {
        console.error(`✘ [ERROR] ${text}`);
        if (location) {
          console.error(`    ${location.file}:${location.line}:${location.column}:`);
        }
      }
      console.log('[watch] build finished');
    });
  },
};

async function main() {
  const ctx = await esbuild.context({
    entryPoints: ['src/extension.ts'],
    bundle: true,
    format: 'cjs',
    minify: production,
    sourcemap: !production,
    sourcesContent: false,
    platform: 'node',
    outfile: 'dist/extension.js',
    external: ['vscode'],
    logLevel: 'warning',
    plugins: [esbuildProblemMatcherPlugin],
  });
  if (watch) {
    await ctx.watch();
  } else {
    await ctx.rebuild();
    await ctx.dispose();
  }
}

main().catch(e => { console.error(e); process.exit(1); });
```

### npm Scripts

```json
{
  "scripts": {
    "vscode:prepublish": "npm run package",
    "compile": "npm run check-types && npm run lint && node esbuild.js",
    "watch": "npm-run-all -p watch:*",
    "watch:esbuild": "node esbuild.js --watch",
    "watch:tsc": "tsc --noEmit --watch --project tsconfig.json",
    "package": "npm run check-types && npm run lint && node esbuild.js --production",
    "compile-tests": "tsc -p . --outDir out",
    "watch-tests": "tsc -p . -w --outDir out",
    "pretest": "npm run compile-tests && npm run compile && npm run lint",
    "check-types": "tsc --noEmit",
    "lint": "eslint src",
    "test": "vscode-test"
  }
}
```

- `check-types` runs `tsc --noEmit` because esbuild strips types without checking them.
- `watch` runs esbuild and tsc in parallel through `npm-run-all`, a dev dependency.
- `compile-tests` compiles the sources and tests into `out/`, where `.vscode-test.mjs` looks for
  them, and `pretest` runs it before every `npm test`. Without it nothing writes `out/test`, and
  the test run finds no files and still passes, because `vscode-test` fails on zero tests only
  with `--fail-zero`.
- `vscode:prepublish` runs automatically during `vsce package` and `vsce publish`.
- `lint` uses ESLint's flat config, `eslint.config.mjs`.

### .vscodeignore

```
.vscode/**
.vscode-test/**
out/**
node_modules/**
src/**
.gitignore
.yarnrc
esbuild.js
vsc-extension-quickstart.md
**/tsconfig.json
**/eslint.config.mjs
**/*.map
**/*.ts
**/.vscode-test.*
```

Everything bundled into `dist/extension.js` is excluded, which keeps the `.vsix` small. `vsce ls`
lists exactly what a package will ship.

### Key Configuration Decisions

- `external: ['vscode']`: the extension host provides the `vscode` module, so it is never bundled
- `format: 'cjs'`: what the generator and the Bundling page emit. The desktop extension host has
  also loaded ESM extensions, declared with `"type": "module"`, since VS Code 1.100
- `platform: 'node'`: desktop extensions run in Node.js, not the browser
- `sourcemap: !production`: maps for development, omitted from the published `.vsix`

---

## TypeScript Configuration

### tsconfig.json

```json
{
  "compilerOptions": {
    "module": "Node16",
    "target": "ES2022",
    "lib": ["ES2022"],
    "types": ["node", "mocha"],
    "rootDir": "src",
    "sourceMap": true,
    "strict": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

TypeScript 6.0 made `types` default to `[]`. Without the `types` entry, `tsc` sees neither Node's
globals such as `console` nor Mocha's `suite` and `test`, and type checking fails. The two entries
need `@types/node` and `@types/mocha` as dev dependencies; match `@types/node` to the Node version
VS Code runs extensions on, which `code --version` does not print but the VS Code About dialog
does.

`compile-tests` writes to `out/` for the test runner. The extension itself runs from `dist/`.

---

## Testing Infrastructure

### Setup

```bash
npm install --save-dev @vscode/test-cli @vscode/test-electron @types/mocha
```

### Configuration (.vscode-test.mjs)

```javascript
import { defineConfig } from '@vscode/test-cli';

export default defineConfig({
  files: 'out/test/**/*.test.js',
  version: 'stable',                    // or 'insiders'
  workspaceFolder: './test-workspace',   // optional test workspace
  launchArgs: ['--disable-extensions'],  // keep other installed extensions out
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

Run one configuration with `npx vscode-test --label unit`; `--label` matches only a configuration
that declares that label. `npx vscode-test --list-configuration` prints the resolved
configuration, including the files it found.

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

## Debugging

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
      "preLaunchTask": "${defaultBuildTask}"
    }
  ]
}
```

Run and debug tests through the Extension Test Runner extension (`ms-vscode.extension-test-runner`).
It reads `.vscode-test.mjs` and lists the tests in the Testing view, so tests need no launch
configuration of their own.

### Tasks Configuration (.vscode/tasks.json)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "watch",
      "dependsOn": ["npm: watch:tsc", "npm: watch:esbuild"],
      "presentation": { "reveal": "never" },
      "group": { "kind": "build", "isDefault": true }
    },
    {
      "type": "npm",
      "script": "watch:esbuild",
      "group": "build",
      "problemMatcher": "$esbuild-watch",
      "isBackground": true,
      "label": "npm: watch:esbuild",
      "presentation": { "group": "watch", "reveal": "never" }
    },
    {
      "type": "npm",
      "script": "watch:tsc",
      "group": "build",
      "problemMatcher": "$tsc-watch",
      "isBackground": true,
      "label": "npm: watch:tsc",
      "presentation": { "group": "watch", "reveal": "never" }
    }
  ]
}
```

The `$esbuild-watch` problem matcher comes from the `connor4312.esbuild-problem-matchers`
extension. List it, with `dbaeumer.vscode-eslint` and `ms-vscode.extension-test-runner`, under
`recommendations` in `.vscode/extensions.json`, as the generator does.

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
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: 22
      - run: npm ci
      - run: npm run check-types
      - run: npm run lint
      - run: xvfb-run -a npm test   # VS Code needs a display on Linux
```

`@vscode/vsce`, `@vscode/test-cli` and `@vscode/test-electron` require Node 22 or later. The
`xvfb-run` wrapper provides a virtual display for the Extension Development Host.

---

## Publishing to Marketplace

### Publisher and Authentication

1. Create a publisher on the Visual Studio Marketplace publisher management page.
2. Publish with a federated identity rather than a stored token. Global Azure DevOps personal
   access tokens, the "All accessible organizations" kind that Marketplace publishing has used,
   retire on December 1, 2026.

**GitHub Actions, trusted publishing.** On the publisher's page, open Trusted Publishing and
create a policy naming the repository owner, the repository, the workflow file under
`.github/workflows`, and the GitHub environment if the job uses one. For a private repository,
run that workflow within 48 hours; the first successful token exchange activates the policy.
Then publish from the workflow with vsce 4.0.2 or later:

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: 22
      - run: npm ci
      - run: npx @vscode/vsce publish --oidc
```

The Marketplace credential lasts 15 minutes, and each GitHub OIDC token can be exchanged once.

**Azure Pipelines, Microsoft Entra ID.** Create an Azure Resource Manager service connection
whose identity belongs to the publisher, and run `vsce publish --azure-credential` in an
`AzureCLI@2` task that uses it.

**Other CI providers and local publishing.** Trusted publishing supports no other OIDC provider.
Until December 1, 2026, a global personal access token with the Marketplace → Manage scope still
works through `vsce login <publisher-id>`, `vsce publish -p <token>`, or the `VSCE_PAT`
environment variable.

### Publishing Commands

```bash
npm install -g @vscode/vsce

vsce package                         # create .vsix without publishing
vsce publish                         # publish with the configured credential
vsce publish minor                   # auto-increment minor version + publish
vsce publish 1.2.0                   # publish specific version
```

Local installation for testing:

```bash
code --install-extension my-extension-0.1.0.vsix
```

Use `code-insiders --install-extension` for Insiders. The install goes to the default profile
unless `--profile <name>` names another. In a WSL or SSH remote a plain shell ignores
`--profile`, and the window's integrated terminal installs into the window's current profile,
as SKILL.md's Platform Notes describe.

### Pre-Publish Checklist

1. Version bumped in `package.json`
2. `CHANGELOG.md` updated
3. `README.md` describes the extension (renders as marketplace page)
4. `vscode:prepublish` script runs successfully
5. `engines.vscode` matches the minimum supported version, and `@types/vscode` is no newer: vsce
   refuses to package when `@types/vscode` is greater than `engines.vscode`
6. `vsce ls` shows only the files the extension needs at runtime

---

## Platform-Specific Builds

For extensions with native dependencies. `vsce package` takes one target per run, and
`vsce publish` takes several:

```bash
# Package one target per run
for target in linux-x64 linux-arm64 darwin-x64 darwin-arm64 win32-x64; do
  vsce package --target "$target"
done

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
    "url": "<repository URL>"
  },
  "sponsor": {
    "url": "<sponsor page URL>"
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
      "url": "<badge image URL>",
      "href": "<link target>",
      "description": "Build Status"
    }
  ]
}
```

vsce accepts badge images only from its list of trusted badge providers, such as shields.io; it
rejects a package whose badge comes from any other host.

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
