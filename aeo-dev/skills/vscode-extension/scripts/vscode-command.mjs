import { execFileSync } from "node:child_process";
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { setTimeout as sleep } from "node:timers/promises";

const [folderArg, command, ...rawArgs] = process.argv.slice(2);
if (!folderArg || !command) {
  console.error("usage: node vscode-command.mjs <workspace folder> <command id> [JSON argument ...]");
  process.exit(2);
}
const folder = path.resolve(folderArg);
const commandArgs = rawArgs.map((a) => JSON.parse(a));
const api = "require('node:module').createRequire(process.execPath)('vscode')";

function extensionHosts() {
  const hosts = [];
  for (const pid of readdirSync("/proc").filter((p) => /^\d+$/.test(p))) {
    let argv;
    try {
      argv = readFileSync(`/proc/${pid}/cmdline`, "utf8").split(/[\0 ]/);
    } catch (error) {
      if (error.code === "ENOENT") continue;
      throw error;
    }
    if (["code", "code-insiders"].includes(path.basename(argv[0])) && argv.includes("--utility-sub-type=node.mojom.NodeService") && argv.includes("--inspect-port=0")) {
      hosts.push(Number(pid));
    }
  }
  return hosts;
}

async function openInspector(pid) {
  const listening = execFileSync("ss", ["-ltnpH"], { encoding: "utf8" })
    .split("\n")
    .filter((line) => line.includes(`pid=${pid},`))
    .map((line) => line.match(/127\.0\.0\.1:(\d+)/)?.[1])
    .filter(Boolean);
  for (const port of listening) {
    const response = await fetch(`http://127.0.0.1:${port}/json/list`, { signal: AbortSignal.timeout(1000) }).catch(() => null);
    if (!response?.ok) continue;
    const targets = await response.json().catch(() => null);
    if (targets?.[0]?.webSocketDebuggerUrl) return targets[0].webSocketDebuggerUrl;
  }
  return null;
}

async function inspectorUrl(pid) {
  for (let attempt = 0; attempt < 20; attempt++) {
    const url = await openInspector(pid);
    if (url) return url;
    await sleep(250);
  }
  throw new Error(`extension host ${pid} opened no inspector after SIGUSR1`);
}

async function closeInspector(pid, url) {
  await evaluate(url, "(() => { const inspector = require('node:inspector'); setTimeout(() => inspector.close(), 500); return true; })()", 10);
  for (let attempt = 0; attempt < 20; attempt++) {
    await sleep(250);
    if (!(await openInspector(pid))) return;
  }
  throw new Error(`extension host ${pid} kept its inspector open`);
}

function evaluate(url, expression, waitSeconds) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(url);
    let answered = false;
    const timer = setTimeout(() => {
      answered = true;
      ws.close();
      resolve({ pending: `no answer within ${waitSeconds}s; the command may be waiting on the window` });
    }, waitSeconds * 1000);
    ws.onopen = () =>
      ws.send(JSON.stringify({ id: 1, method: "Runtime.evaluate", params: { expression, includeCommandLineAPI: true, awaitPromise: true, returnByValue: true } }));
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.id !== 1) return;
      answered = true;
      clearTimeout(timer);
      ws.close();
      const { result, exceptionDetails } = message.result;
      if (exceptionDetails) resolve({ exception: exceptionDetails.exception?.description ?? exceptionDetails.text });
      else resolve({ value: result.value });
    };
    ws.onclose = () => {
      clearTimeout(timer);
      if (!answered) resolve({ closed: "the inspector connection closed before answering" });
    };
    ws.onerror = () => {
      if (!answered) reject(new Error(`inspector connection failed: ${url}`));
    };
  });
}

function running(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    if (error.code === "ESRCH") return false;
    throw error;
  }
}

const seen = [];
for (const pid of extensionHosts()) {
  process.kill(pid, "SIGUSR1");
  const url = await inspectorUrl(pid);
  const query = await evaluate(url, `${api}.workspace.workspaceFolders?.map((f) => f.uri.fsPath) ?? []`, 10);
  if (!Array.isArray(query.value)) throw new Error(`extension host ${pid} did not list its folders: ${JSON.stringify(query)}`);
  seen.push(...query.value);
  if (!query.value.includes(folder)) {
    await closeInspector(pid, url);
    continue;
  }
  const outcome = await evaluate(url, `${api}.commands.executeCommand(${JSON.stringify(command)}, ...${JSON.stringify(commandArgs)})`, 10);
  await sleep(3000);
  const extensionHostExited = !running(pid);
  if (!extensionHostExited) await closeInspector(pid, url);
  console.log(JSON.stringify({ folder, command, extensionHost: pid, extensionHostExited, ...outcome }));
  process.exit(outcome.exception && !extensionHostExited ? 3 : 0);
}
console.error(`no VS Code window has ${folder} open; open folders: ${JSON.stringify(seen)}`);
process.exit(1);
