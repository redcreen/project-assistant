"use strict";

const cp = require("child_process");
const fs = require("fs");
const path = require("path");
const net = require("net");
const vscode = require("vscode");

const COMMAND_ID = "redcreen.workspaceDocBrowser.open";
const OUTPUT_NAME = "Workspace Doc Browser";
const BUTTON_TEXT = "$(globe) Browse Docs";
const LIVE_TEXT = "$(globe) Docs Live";
const STARTING_TEXT = "$(sync~spin) Starting Docs";
const OPENING_TEXT = "$(sync~spin) Opening Docs";
const DOCS_STARTUP_LOG_REVEAL_MS = 2500;
const DOCS_STARTUP_READY_ATTEMPTS = 120;
const DOCS_STARTUP_READY_DELAY_MS = 100;
const TREE_REFRESH_MS = 3000;
const FILE_REFRESH_MS = 1200;

class WorkspaceDocBrowser {
  constructor(context) {
    this.context = context;
    this.output = vscode.window.createOutputChannel(OUTPUT_NAME);
    this.statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 90);
    this.session = null;
    this.pendingOpen = null;
  }

  activate() {
    this.context.subscriptions.push(
      this.output,
      this.statusBar,
      vscode.commands.registerCommand(COMMAND_ID, (targetUri) => this.open(targetUri)),
      vscode.workspace.onDidChangeWorkspaceFolders(() => this.updateStatusBar()),
      vscode.window.onDidChangeActiveTextEditor(() => this.updateStatusBar()),
      { dispose: () => this.disposeSession() },
    );
    this.updateStatusBar();
  }

  normalizeTargetUri(targetUri) {
    if (targetUri && targetUri.scheme === "file") {
      return targetUri;
    }
    const editor = vscode.window.activeTextEditor;
    if (editor && editor.document && editor.document.uri.scheme === "file") {
      return editor.document.uri;
    }
    return null;
  }

  getWorkspaceRoot(targetUri) {
    const normalizedTargetUri = this.normalizeTargetUri(targetUri);
    if (normalizedTargetUri) {
      const folder = vscode.workspace.getWorkspaceFolder(normalizedTargetUri);
      if (folder) {
        return folder.uri.fsPath;
      }
    }
    const folder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
    return folder ? folder.uri.fsPath : null;
  }

  pickDefaultMarkdownPath(workspaceRoot) {
    const preferred = [
      "README.md",
      "README.zh-CN.md",
      "docs/README.md",
      "docs/README.zh-CN.md",
      "index.md",
    ];
    for (const relativePath of preferred) {
      const absolutePath = path.join(workspaceRoot, relativePath);
      if (isMarkdownFile(path.basename(relativePath), absolutePath)) {
        return normalizeSlashes(relativePath);
      }
    }
    return findFirstMarkdownPath(workspaceRoot, "");
  }

  getTargetDescriptor(workspaceRoot, targetUri) {
    const normalizedTargetUri = this.normalizeTargetUri(targetUri);
    if (normalizedTargetUri) {
      const relativePath = normalizeSlashes(path.relative(workspaceRoot, normalizedTargetUri.fsPath));
      if (relativePath && !relativePath.startsWith("..") && !path.isAbsolute(relativePath)) {
        return {
          relativePath,
          isMarkdown: /\.md$/i.test(relativePath),
        };
      }
    }
    const fallbackPath = this.pickDefaultMarkdownPath(workspaceRoot);
    if (!fallbackPath) {
      return null;
    }
    return {
      relativePath: fallbackPath,
      isMarkdown: true,
    };
  }

  getBootstrapUrl(baseUrl, workspaceRoot, relativePath) {
    const bootstrapUrl = new URL("/__workspace_doc_browser__/bootstrap", `${String(baseUrl || "").replace(/\/$/, "")}/`);
    bootstrapUrl.searchParams.set("path", relativePath);
    bootstrapUrl.searchParams.set("workspace", path.basename(workspaceRoot));
    return bootstrapUrl.toString();
  }

  getTargetUrl(baseUrl, workspaceRoot, targetUri) {
    const descriptor = this.getTargetDescriptor(workspaceRoot, targetUri);
    if (!descriptor) {
      return `${String(baseUrl || "").replace(/\/$/, "")}/`;
    }
    if (descriptor.isMarkdown) {
      return this.getBootstrapUrl(baseUrl, workspaceRoot, descriptor.relativePath);
    }
    return new URL(encodePathSegments(descriptor.relativePath), `${String(baseUrl || "").replace(/\/$/, "")}/`).toString();
  }

  updateStatusBar() {
    const workspaceRoot = this.getWorkspaceRoot();
    if (!workspaceRoot) {
      this.statusBar.hide();
      return;
    }
    const isPending = Boolean(this.pendingOpen && this.pendingOpen.workspaceRoot === workspaceRoot);
    const isLive = Boolean(this.session && this.session.workspaceRoot === workspaceRoot && this.isSessionLive(this.session));
    this.statusBar.text = isPending
      ? (this.pendingOpen.kind === "start" ? STARTING_TEXT : OPENING_TEXT)
      : (isLive ? LIVE_TEXT : BUTTON_TEXT);
    this.statusBar.tooltip = isPending
      ? this.pendingOpen.detail
      : isLive
        ? `Open the live browser preview for ${path.basename(workspaceRoot)}`
        : `Open ${path.basename(workspaceRoot)} in a browser as rendered Markdown`;
    this.statusBar.command = COMMAND_ID;
    this.statusBar.show();
  }

  setPendingOpen(workspaceRoot, detail, kind) {
    this.clearPendingOpen();
    const pending = {
      workspaceRoot,
      detail,
      kind,
      revealTimer: setTimeout(() => {
        if (this.pendingOpen !== pending) {
          return;
        }
        this.output.appendLine(`[pending] ${detail}`);
        this.output.show(false);
        vscode.window.setStatusBarMessage(`Workspace Doc Browser: ${detail}`, 4000);
      }, DOCS_STARTUP_LOG_REVEAL_MS),
    };
    this.pendingOpen = pending;
    this.updateStatusBar();
  }

  clearPendingOpen() {
    if (!this.pendingOpen) {
      return;
    }
    if (this.pendingOpen.revealTimer) {
      clearTimeout(this.pendingOpen.revealTimer);
    }
    this.pendingOpen = null;
    this.updateStatusBar();
  }

  announceManualAction(workspaceRoot, kind) {
    const workspaceName = path.basename(workspaceRoot);
    const message = kind === "start"
      ? `Workspace Doc Browser: starting docs for ${workspaceName}…`
      : `Workspace Doc Browser: opening docs for ${workspaceName}…`;
    vscode.window.showInformationMessage(message);
    vscode.window.setStatusBarMessage(message, 4000);
  }

  async openBrowserUrl(url, workspaceRoot, contextLabel, session) {
    this.output.appendLine(`[browser-open] ${contextLabel}: ${url}`);
    const opened = await vscode.env.openExternal(vscode.Uri.parse(url));
    if (session && this.session === session) {
      session.browserOpened = Boolean(opened);
      this.updateStatusBar();
    }
    if (!opened) {
      this.output.appendLine(`[browser-open-error] ${contextLabel}: VS Code could not hand the URL to the system browser.`);
      this.output.show(true);
      vscode.window.showWarningMessage(
        `Workspace Doc Browser: ${contextLabel} for ${path.basename(workspaceRoot)} could not be opened in your browser. Check the Workspace Doc Browser output.`,
      );
    }
    return opened;
  }

  async openExistingSession(session, workspaceRoot, targetUri) {
    if (!session || !this.isSessionAlive(session)) {
      return false;
    }
    const targetUrl = this.getTargetUrl(session.baseUrl, workspaceRoot, targetUri);
    session.targetUri = this.normalizeTargetUri(targetUri);
    this.setPendingOpen(workspaceRoot, `Opening docs preview for ${path.basename(workspaceRoot)}…`, "open");
    try {
      await this.openBrowserUrl(targetUrl, workspaceRoot, "the docs preview", session);
    } finally {
      this.clearPendingOpen();
    }
    return true;
  }

  async startSession(workspaceRoot, targetUri) {
    this.setPendingOpen(workspaceRoot, `Starting docs preview for ${path.basename(workspaceRoot)}…`, "start");

    try {
      const port = await findFreePort();
      this.disposeSession();

      const baseUrl = `http://127.0.0.1:${port}/`;
      const rawServerScript = buildRawFileServerScript(workspaceRoot, port);
      const rawProcess = cp.spawn(process.execPath, ["-e", rawServerScript], {
        cwd: workspaceRoot,
        env: process.env,
        stdio: ["ignore", "pipe", "pipe"],
      });

      const session = {
        workspaceRoot,
        baseUrl,
        port,
        browserOpened: false,
        targetUri: this.normalizeTargetUri(targetUri),
        process: rawProcess,
      };
      this.session = session;
      this.updateStatusBar();
      this.output.appendLine(`[start] ${workspaceRoot}`);
      this.output.appendLine(`[raw] ${baseUrl}`);

      rawProcess.stdout.on("data", (chunk) => {
        this.output.append(chunk.toString());
      });
      rawProcess.stderr.on("data", (chunk) => {
        this.output.append(chunk.toString());
      });
      rawProcess.on("error", (error) => {
        this.clearPendingOpen();
        this.output.appendLine(`[error] ${String(error)}`);
        vscode.window.showErrorMessage(`Workspace Doc Browser: ${String(error)}`);
        if (this.session === session) {
          this.session = null;
          this.updateStatusBar();
        }
      });
      rawProcess.on("exit", (code, signal) => {
        this.clearPendingOpen();
        this.output.appendLine(`[raw-exit] code=${code} signal=${signal}`);
        const wasCurrentSession = this.session === session;
        if (wasCurrentSession) {
          this.session = null;
          this.updateStatusBar();
        }
        if (code && code !== 0) {
          vscode.window.showErrorMessage(`Workspace Doc Browser: preview backend exited with code ${code}.`);
          this.output.show(true);
        } else if (wasCurrentSession && signal !== "SIGTERM") {
          vscode.window.showWarningMessage("Workspace Doc Browser: preview stopped.");
        }
      });

      await waitForPortReady(port, DOCS_STARTUP_READY_ATTEMPTS, DOCS_STARTUP_READY_DELAY_MS);
      if (this.session !== session) {
        return false;
      }
      const targetUrl = this.getTargetUrl(baseUrl, workspaceRoot, targetUri);
      await this.openBrowserUrl(targetUrl, workspaceRoot, "the docs preview", session);
      return true;
    } catch (error) {
      this.output.appendLine(`[open-error] ${String(error)}`);
      this.output.show(true);
      vscode.window.showWarningMessage(
        `Workspace Doc Browser: the docs server for ${path.basename(workspaceRoot)} did not become ready yet. Check the Workspace Doc Browser output for details.`,
      );
      return false;
    } finally {
      this.clearPendingOpen();
    }
  }

  async open(targetUri) {
    const workspaceRoot = this.getWorkspaceRoot(targetUri);
    if (!workspaceRoot) {
      vscode.window.showWarningMessage("Workspace Doc Browser: open a local folder first.");
      return;
    }

    this.announceManualAction(
      workspaceRoot,
      this.session && this.session.workspaceRoot === workspaceRoot && this.isSessionAlive(this.session) ? "open" : "start",
    );

    if (this.session && this.session.workspaceRoot === workspaceRoot && this.isSessionAlive(this.session)) {
      await this.openExistingSession(this.session, workspaceRoot, targetUri);
      return;
    }

    await this.startSession(workspaceRoot, targetUri);
  }

  isSessionAlive(session = this.session) {
    return Boolean(
      session &&
      session.process &&
      !session.process.killed &&
      session.process.exitCode === null &&
      session.process.signalCode === null,
    );
  }

  isSessionLive(session = this.session) {
    return Boolean(this.isSessionAlive(session) && session && session.browserOpened);
  }

  disposeSession() {
    if (!this.session) {
      return;
    }
    const { process } = this.session;
    this.session = null;
    if (process && !process.killed) {
      try {
        process.kill("SIGTERM");
      } catch {}
    }
  }
}

function normalizeSlashes(value) {
  return String(value || "").replace(/\\/g, "/");
}

function encodePathSegments(value) {
  return normalizeSlashes(String(value || ""))
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/");
}

function isMarkdownFile(name, absolutePath) {
  if (!/\.md$/i.test(name)) {
    return false;
  }
  try {
    return fs.statSync(absolutePath).isFile();
  } catch {
    return false;
  }
}

function shouldIgnoreEntry(name, isDirectory, options = {}) {
  const includeDotfiles = Boolean(options.includeDotfiles);
  if (!name || name === ".DS_Store") {
    return true;
  }
  if (!includeDotfiles && name.startsWith(".") && name !== ".github") {
    return true;
  }
  if (isDirectory) {
    return ["node_modules", ".git", ".vscode", ".idea", "__pycache__", ".mkdocs", ".mkdocs-site", "dist"].includes(name);
  }
  return false;
}

function compareEntries(left, right) {
  if (left.isDirectory() && !right.isDirectory()) {
    return -1;
  }
  if (!left.isDirectory() && right.isDirectory()) {
    return 1;
  }
  return left.name.localeCompare(right.name, undefined, { numeric: true, sensitivity: "base" });
}

function findFirstMarkdownPath(workspaceRoot, relativeDir) {
  const absoluteDir = path.join(workspaceRoot, relativeDir);
  let entries = [];
  try {
    entries = fs.readdirSync(absoluteDir, { withFileTypes: true })
      .filter((entry) => !shouldIgnoreEntry(entry.name, entry.isDirectory(), { includeDotfiles: false }))
      .sort(compareEntries);
  } catch {
    return "";
  }

  for (const entry of entries) {
    const relativePath = normalizeSlashes(path.posix.join(relativeDir, entry.name));
    const absolutePath = path.join(workspaceRoot, relativePath);
    if (entry.isDirectory()) {
      const childPath = findFirstMarkdownPath(workspaceRoot, relativePath);
      if (childPath) {
        return childPath;
      }
      continue;
    }
    if (entry.isFile() && isMarkdownFile(entry.name, absolutePath)) {
      return relativePath;
    }
  }
  return "";
}

function buildRawFileServerScript(workspaceRoot, port) {
  return `
const http = require("http");
const fs = require("fs");
const path = require("path");

const root = ${JSON.stringify(workspaceRoot)};
const port = ${Number(port)};
const TREE_REFRESH_MS = ${TREE_REFRESH_MS};
const FILE_REFRESH_MS = ${FILE_REFRESH_MS};

const textTypes = new Map([
  [".md", "text/markdown; charset=utf-8"],
  [".txt", "text/plain; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".ts", "text/plain; charset=utf-8"],
  [".py", "text/x-python; charset=utf-8"],
  [".sh", "text/x-shellscript; charset=utf-8"],
  [".yml", "text/yaml; charset=utf-8"],
  [".yaml", "text/yaml; charset=utf-8"],
  [".toml", "text/plain; charset=utf-8"],
  [".ini", "text/plain; charset=utf-8"],
  [".cfg", "text/plain; charset=utf-8"],
  [".conf", "text/plain; charset=utf-8"],
  [".xml", "application/xml; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".csv", "text/csv; charset=utf-8"],
  [".env", "text/plain; charset=utf-8"],
  [".gitignore", "text/plain; charset=utf-8"],
  [".dockerfile", "text/plain; charset=utf-8"],
]);

function send(res, status, body, contentType) {
  res.writeHead(status, {
    "Content-Type": contentType,
    "Access-Control-Allow-Origin": "*",
    "Cache-Control": "no-store",
  });
  res.end(body);
}

function normalizeSlashes(value) {
  return String(value || "").replace(/\\\\/g, "/");
}

function shouldIgnoreEntry(name, isDirectory, includeDotfiles) {
  if (!name || name === ".DS_Store") {
    return true;
  }
  if (!includeDotfiles && name.startsWith(".") && name !== ".github") {
    return true;
  }
  if (isDirectory) {
    return ["node_modules", ".git", ".vscode", ".idea", "__pycache__", ".mkdocs", ".mkdocs-site", "dist"].includes(name);
  }
  return false;
}

function compareEntries(left, right) {
  if (left.isDirectory() && !right.isDirectory()) {
    return -1;
  }
  if (!left.isDirectory() && right.isDirectory()) {
    return 1;
  }
  return left.name.localeCompare(right.name, undefined, { numeric: true, sensitivity: "base" });
}

function buildRepoTree(relativeDir) {
  const absoluteDir = path.join(root, relativeDir);
  let entries = [];
  try {
    entries = fs.readdirSync(absoluteDir, { withFileTypes: true })
      .filter((entry) => !shouldIgnoreEntry(entry.name, entry.isDirectory(), true))
      .sort(compareEntries);
  } catch {
    return [];
  }

  const items = [];
  for (const entry of entries) {
    const relativePath = normalizeSlashes(path.posix.join(relativeDir, entry.name));
    const absolutePath = path.join(root, relativePath);
    if (entry.isDirectory()) {
      items.push({
        title: entry.name + "/",
        kind: "directory",
        path: relativePath,
        children: buildRepoTree(relativePath),
      });
      continue;
    }
    if (!entry.isFile()) {
      continue;
    }
    items.push({
      title: entry.name,
      kind: /\\.md$/i.test(entry.name) ? "markdown" : "file",
      sourcePath: relativePath,
    });
  }
  return items;
}

http.createServer((req, res) => {
  if (!req.url) {
    return send(res, 400, "Bad Request", "text/plain; charset=utf-8");
  }
  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "*",
    });
    return res.end();
  }

  const parsed = new URL(req.url, "http://127.0.0.1");
  if (parsed.pathname === "/__workspace_doc_browser__/tree") {
    return send(res, 200, JSON.stringify(buildRepoTree("")), "application/json; charset=utf-8");
  }
  if (parsed.pathname === "/__workspace_doc_browser__/bootstrap") {
    const relativePath = String(parsed.searchParams.get("path") || "");
    const workspace = String(parsed.searchParams.get("workspace") || "Workspace Docs");
    return send(
      res,
      200,
      (${buildBootstrapViewerHtml.toString()})(workspace, relativePath, TREE_REFRESH_MS, FILE_REFRESH_MS),
      "text/html; charset=utf-8",
    );
  }

  const relativePath = decodeURIComponent(parsed.pathname.replace(/^\\/+/, ""));
  const target = path.resolve(root, relativePath);
  if (!target.startsWith(path.resolve(root))) {
    return send(res, 403, "Forbidden", "text/plain; charset=utf-8");
  }

  fs.stat(target, (error, stat) => {
    if (error || !stat.isFile()) {
      return send(res, 404, "Not Found", "text/plain; charset=utf-8");
    }
    const ext = path.extname(target).toLowerCase();
    const type = textTypes.get(ext) || textTypes.get(path.basename(target).toLowerCase()) || "application/octet-stream";
    fs.readFile(target, type.includes("charset=utf-8") ? "utf8" : null, (readError, data) => {
      if (readError) {
        return send(res, 500, String(readError), "text/plain; charset=utf-8");
      }
      send(res, 200, data, type);
    });
  });
}).listen(port, "127.0.0.1", () => {
  console.log("[raw-server] listening on http://127.0.0.1:" + port);
});
`;
}

function buildBootstrapViewerHtml(workspaceName, relativePath, treeRefreshMs, fileRefreshMs) {
  function escapeBootstrapHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  const title = escapeBootstrapHtml(String(workspaceName || "Workspace Docs"));
  const fileLabel = escapeBootstrapHtml(String(relativePath || ""));
  const safeRelativePath = JSON.stringify(String(relativePath || ""));
  const safeWorkspaceName = JSON.stringify(String(workspaceName || "Workspace Docs"));
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  <style>
    :root {
      --bg: #f3f5f7;
      --panel: #ffffff;
      --border: #d0d7de;
      --text: #1f2328;
      --muted: #59636e;
      --link: #0969da;
      --code-bg: rgba(175, 184, 193, 0.2);
      --pre-bg: #f6f8fa;
      --sidebar-hover: #eef5ff;
      --quote-bg: #fbfcfd;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 16px/1.72 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI Variable", "Segoe UI", Helvetica, Arial, sans-serif;
      text-rendering: optimizeLegibility;
    }
    .shell {
      width: min(1400px, calc(100vw - 32px));
      margin: 18px auto;
    }
    .content, .sidebar {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(31, 35, 40, 0.04);
    }
    .layout {
      display: grid;
      grid-template-columns: 286px minmax(0, 1fr);
      gap: 18px;
      align-items: start;
    }
    body.sidebar-collapsed .layout {
      grid-template-columns: 56px minmax(0, 1fr);
    }
    .sidebar {
      position: sticky;
      top: 16px;
      overflow: hidden;
    }
    .sidebar-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 16px;
      font-weight: 700;
      border-bottom: 1px solid var(--border);
      background: linear-gradient(to bottom, #ffffff, #fafbfc);
    }
    .sidebar-title {
      white-space: nowrap;
    }
    .sidebar-toggle {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      margin-left: 12px;
      padding: 0;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #ffffff;
      color: var(--muted);
      cursor: pointer;
      font: inherit;
      line-height: 1;
    }
    .sidebar-toggle:hover {
      color: var(--link);
      background: var(--sidebar-hover);
    }
    .sidebar-body {
      max-height: calc(100vh - 64px);
      overflow: auto;
      padding: 10px 0 12px;
    }
    body.sidebar-collapsed .sidebar-header {
      justify-content: center;
      padding: 14px 10px;
      border-bottom: 0;
    }
    body.sidebar-collapsed .sidebar-title,
    body.sidebar-collapsed .sidebar-body {
      display: none;
    }
    body.sidebar-collapsed .sidebar-toggle {
      margin-left: 0;
    }
    .tree,
    .tree ul {
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .tree li {
      margin: 0;
    }
    .tree ul {
      padding-left: 18px;
    }
    .tree details {
      margin: 0;
    }
    .tree summary {
      cursor: pointer;
      padding: 7px 16px;
      color: var(--muted);
      user-select: none;
      font-size: 14px;
      line-height: 1.45;
    }
    .tree a {
      display: block;
      padding: 7px 16px;
      color: var(--text);
      text-decoration: none;
      border-left: 2px solid transparent;
      font-size: 14px;
      line-height: 1.45;
      word-break: break-word;
    }
    .tree a:hover {
      background: var(--sidebar-hover);
      color: var(--link);
    }
    .tree a.active {
      color: var(--link);
      font-weight: 600;
      border-left-color: var(--link);
      background: rgba(9, 105, 218, 0.08);
    }
    .content {
      padding: 32px 36px 40px;
      min-height: 70vh;
    }
    .content-shell {
      width: min(860px, 100%);
    }
    .file-meta {
      margin-bottom: 22px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    .markdown-body {
      font-size: 17px;
    }
    .markdown-body > :first-child {
      margin-top: 0;
    }
    .markdown-body > :last-child {
      margin-bottom: 0;
    }
    .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6 {
      line-height: 1.25;
      margin-top: 1.8em;
      margin-bottom: 0.7em;
      font-weight: 700;
      letter-spacing: -0.02em;
      scroll-margin-top: 24px;
    }
    .markdown-body h1 {
      font-size: 2.2rem;
    }
    .markdown-body h2 {
      font-size: 1.72rem;
    }
    .markdown-body h3 {
      font-size: 1.35rem;
    }
    .markdown-body h4 {
      font-size: 1.12rem;
    }
    .markdown-body h5, .markdown-body h6 {
      font-size: 1rem;
    }
    .markdown-body h1, .markdown-body h2 {
      padding-bottom: 0.3em;
      border-bottom: 1px solid var(--border);
    }
    .markdown-body p, .markdown-body ul, .markdown-body ol, .markdown-body blockquote, .markdown-body pre, .markdown-body table, .markdown-body hr {
      margin-top: 0;
      margin-bottom: 1.15em;
    }
    .markdown-body ul, .markdown-body ol {
      padding-left: 1.45em;
    }
    .markdown-body li {
      margin: 0.35em 0;
    }
    .markdown-body li > p {
      margin-bottom: 0.45em;
    }
    .markdown-body a {
      color: var(--link);
      text-decoration: none;
      text-underline-offset: 0.18em;
      word-break: break-word;
    }
    .markdown-body a:hover {
      text-decoration: underline;
    }
    .markdown-body strong {
      font-weight: 700;
    }
    .markdown-body hr {
      border: 0;
      border-top: 1px solid var(--border);
    }
    .markdown-body code {
      padding: 0.2em 0.4em;
      font-size: 0.88em;
      background: var(--code-bg);
      border-radius: 6px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }
    .markdown-body pre {
      padding: 18px 20px;
      overflow: auto;
      background: var(--pre-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      font-size: 14px;
      line-height: 1.58;
    }
    .markdown-body pre code {
      padding: 0;
      background: transparent;
      border-radius: 0;
      white-space: pre;
    }
    .markdown-body blockquote {
      padding: 0.12em 1.05em;
      color: var(--muted);
      border-left: 0.25em solid var(--border);
      background: var(--quote-bg);
      border-radius: 0 10px 10px 0;
    }
    .markdown-body blockquote > :last-child {
      margin-bottom: 0;
    }
    .markdown-body .table-wrap {
      width: 100%;
      overflow-x: auto;
      margin-bottom: 1.15em;
    }
    .markdown-body .table-wrap:last-child {
      margin-bottom: 0;
    }
    .markdown-body table {
      width: 100%;
      border-collapse: collapse;
      border-spacing: 0;
      table-layout: fixed;
    }
    .markdown-body th,
    .markdown-body td {
      padding: 10px 12px;
      border: 1px solid var(--border);
      text-align: left;
      vertical-align: top;
      white-space: normal;
      overflow-wrap: anywhere;
      word-break: break-word;
    }
    .markdown-body th {
      background: #f6f8fa;
      font-weight: 600;
    }
    .markdown-body td code,
    .markdown-body th code {
      white-space: break-spaces;
      word-break: break-word;
    }
    .markdown-body img {
      display: block;
      max-width: 100%;
      height: auto;
      margin: 1.2em 0;
      border-radius: 10px;
    }
    .markdown-body .mermaid-diagram {
      margin: 1.2em 0;
      padding: 16px 18px;
      overflow-x: auto;
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 10px;
    }
    .markdown-body .mermaid-diagram .mermaid {
      width: max-content;
      min-width: 100%;
    }
    .markdown-body .mermaid-diagram svg {
      display: block;
      height: auto;
      max-width: none;
    }
    .markdown-body .mermaid-diagram.mermaid-error .mermaid {
      color: var(--muted);
      font: 14px/1.58 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      white-space: pre;
    }
    .markdown-body .empty-state,
    .markdown-body .error-state {
      color: var(--muted);
      font-size: 15px;
    }
    @media (max-width: 900px) {
      .layout {
        grid-template-columns: 1fr;
      }
      body.sidebar-collapsed .layout {
        grid-template-columns: 1fr;
      }
      .sidebar {
        position: static;
      }
      body.sidebar-collapsed .sidebar {
        display: none;
      }
      .sidebar-body {
        max-height: none;
      }
      .content {
        padding: 24px 20px 28px;
      }
      .markdown-body {
        font-size: 16px;
      }
      .markdown-body h1 {
        font-size: 1.9rem;
      }
      .markdown-body h2 {
        font-size: 1.5rem;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="layout">
      <aside id="sidebar" class="sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">Files</span>
          <button id="sidebar-toggle" class="sidebar-toggle" type="button" aria-label="Collapse file tree" title="Collapse file tree">◀</button>
        </div>
        <div id="sidebar-body" class="sidebar-body"></div>
      </aside>
      <article id="content" class="content">
        <div class="content-shell">
          <div class="file-meta">${fileLabel || "Current markdown file"}</div>
          <div class="markdown-body">
            <p class="empty-state">Loading markdown preview…</p>
          </div>
        </div>
      </article>
    </div>
  </div>
  <script>
    const relativePath = ${safeRelativePath};
    const workspaceName = ${safeWorkspaceName};
    const treeRefreshMs = ${Number(treeRefreshMs)};
    const fileRefreshMs = ${Number(fileRefreshMs)};
    const content = document.getElementById("content");
    const sidebar = document.getElementById("sidebar");
    const sidebarBody = document.getElementById("sidebar-body");
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const mermaidScriptUrl = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js";
    let lastMarkdown = "";
    let lastTreeJson = "";
    let mermaidApi = null;
    let mermaidLoadPromise = null;
    const openFolders = new Set();
    const sidebarStateKey = "workspace-doc-browser.sidebar:" + workspaceName;

    function escapeHtml(value) {
      return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    }

    function encodePath(pathValue) {
      return String(pathValue || "")
        .split("/")
        .map((segment) => encodeURIComponent(segment))
        .join("/");
    }

    function isExternalHref(value) {
      return /^(https?:|mailto:|tel:|data:)/i.test(String(value || "").trim());
    }

    function splitHref(value) {
      const raw = String(value || "");
      const index = raw.indexOf("#");
      if (index === -1) {
        return { pathPart: raw, hashPart: "" };
      }
      return {
        pathPart: raw.slice(0, index),
        hashPart: raw.slice(index + 1),
      };
    }

    function resolveRelativePath(basePath, targetPath) {
      const normalizedBase = String(basePath || "").replace(/^\\/+/, "");
      const normalizedTarget = String(targetPath || "").replace(/^\\/+/, "");
      const baseSegments = normalizedBase.split("/").filter(Boolean);
      if (baseSegments.length) {
        baseSegments.pop();
      }
      for (const segment of normalizedTarget.split("/")) {
        if (!segment || segment === ".") {
          continue;
        }
        if (segment === "..") {
          if (baseSegments.length) {
            baseSegments.pop();
          }
          continue;
        }
        baseSegments.push(segment);
      }
      return baseSegments.join("/");
    }

    function bootstrapHref(sourcePath, hashPart = "") {
      const params = new URLSearchParams();
      params.set("path", sourcePath);
      params.set("workspace", workspaceName);
      return "/__workspace_doc_browser__/bootstrap?" + params.toString() + (hashPart ? "#" + encodeURIComponent(hashPart) : "");
    }

    function rawFileHref(sourcePath, hashPart = "") {
      return "/" + encodePath(sourcePath) + (hashPart ? "#" + encodeURIComponent(hashPart) : "");
    }

    function resolveDocHref(href) {
      const raw = String(href || "").trim();
      if (!raw) {
        return "";
      }
      if (isExternalHref(raw)) {
        return raw;
      }
      const { pathPart, hashPart } = splitHref(raw);
      if (!pathPart && hashPart) {
        return "#" + encodeURIComponent(hashPart);
      }
      const resolvedPath = pathPart.startsWith("/")
        ? pathPart.replace(/^\\/+/, "")
        : resolveRelativePath(relativePath, pathPart);
      if (/\\.md$/i.test(resolvedPath)) {
        return bootstrapHref(resolvedPath, hashPart);
      }
      return rawFileHref(resolvedPath, hashPart);
    }

    function slugifyHeading(value, seen) {
      let slug = String(value || "")
        .trim()
        .toLowerCase()
        .replace(/[^\u4e00-\u9fff\\w\\- ]+/g, "")
        .replace(/\\s+/g, "-")
        .replace(/-+/g, "-")
        .replace(/^-|-$/g, "");
      if (!slug) {
        slug = "section";
      }
      const count = seen[slug] || 0;
      seen[slug] = count + 1;
      return count ? slug + "-" + count : slug;
    }

    function renderInline(value) {
      let text = escapeHtml(value);
      text = text.replace(/!\\[([^\\]]*)\\]\\(([^)]+)\\)/g, (_, alt, href) => '<img alt="' + escapeHtml(alt) + '" src="' + escapeHtml(resolveDocHref(href)) + '">');
      text = text.replace(/\\\`([^\\\`]+)\\\`/g, "<code>$1</code>");
      text = text.replace(/\\*\\*([^*]+)\\*\\*/g, "<strong>$1</strong>");
      text = text.replace(/\\*([^*]+)\\*/g, "<em>$1</em>");
      text = text.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, (_, label, href) => '<a href="' + escapeHtml(resolveDocHref(href)) + '">' + label + '</a>');
      return text;
    }

    function mermaidConfig() {
      return {
        startOnLoad: false,
        securityLevel: "loose",
        theme: "default",
        fontFamily: 'ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI Variable", "Segoe UI", Helvetica, Arial, sans-serif',
      };
    }

    function ensureMermaid() {
      if (mermaidApi) {
        return Promise.resolve(mermaidApi);
      }
      if (window.mermaid) {
        mermaidApi = window.mermaid;
        mermaidApi.initialize(mermaidConfig());
        return Promise.resolve(mermaidApi);
      }
      if (mermaidLoadPromise) {
        return mermaidLoadPromise;
      }
      mermaidLoadPromise = new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = mermaidScriptUrl;
        script.async = true;
        script.dataset.workspaceDocBrowserMermaid = "1";
        script.onload = () => {
          if (!window.mermaid) {
            reject(new Error("Mermaid script loaded, but Mermaid did not initialize."));
            return;
          }
          mermaidApi = window.mermaid;
          mermaidApi.initialize(mermaidConfig());
          resolve(mermaidApi);
        };
        script.onerror = () => reject(new Error("Failed to load Mermaid renderer."));
        document.head.appendChild(script);
      });
      return mermaidLoadPromise;
    }

    async function renderMermaidDiagrams() {
      const nodes = Array.from(content.querySelectorAll(".mermaid-diagram .mermaid"));
      if (!nodes.length) {
        return;
      }
      try {
        const mermaid = await ensureMermaid();
        await mermaid.run({ nodes });
      } catch {
        content.querySelectorAll(".mermaid-diagram").forEach((container) => {
          container.classList.add("mermaid-error");
        });
      }
    }

    function renderMarkdown(text) {
      const lines = String(text || "").replace(/\\r\\n/g, "\\n").split("\\n");
      const output = [];
      let paragraph = [];
      let listItems = [];
      let listType = "";
      let inCode = false;
      let codeLines = [];
      let codeLanguage = "";
      const headingIds = Object.create(null);

      function flushParagraph() {
        if (paragraph.length) {
          output.push("<p>" + renderInline(paragraph.join(" ")) + "</p>");
          paragraph = [];
        }
      }

      function flushList() {
        if (listItems.length) {
          output.push("<" + listType + ">" + listItems.join("") + "</" + listType + ">");
          listItems = [];
          listType = "";
        }
      }

      function flushCode() {
        if (inCode) {
          const codeText = codeLines.join("\\n");
          if (String(codeLanguage || "").toLowerCase() === "mermaid") {
            output.push('<div class="mermaid-diagram"><div class="mermaid">' + escapeHtml(codeText) + "</div></div>");
          } else {
            const languageClass = codeLanguage ? ' class=\\"language-' + escapeHtml(codeLanguage) + '\\"' : "";
            output.push("<pre><code" + languageClass + ">" + escapeHtml(codeText) + "</code></pre>");
          }
          inCode = false;
          codeLines = [];
          codeLanguage = "";
        }
      }

      function isHorizontalRule(line) {
        return /^\\s{0,3}([-*_])(\\s*\\1){2,}\\s*$/.test(line);
      }

      function isTableDivider(line) {
        return /^\\s*\\|?(\\s*:?-{3,}:?\\s*\\|)+\\s*:?-{3,}:?\\s*\\|?\\s*$/.test(line);
      }

      function parseTableRow(line) {
        const trimmed = String(line || "").trim().replace(/^\\|/, "").replace(/\\|$/, "");
        return trimmed.split("|").map((cell) => cell.trim());
      }

      function renderTable(headerCells, rows) {
        const headerHtml = "<tr>" + headerCells.map((cell) => "<th>" + renderInline(cell) + "</th>").join("") + "</tr>";
        const bodyHtml = rows.map((row) => "<tr>" + row.map((cell) => "<td>" + renderInline(cell) + "</td>").join("") + "</tr>").join("");
        return '<div class="table-wrap"><table><thead>' + headerHtml + "</thead><tbody>" + bodyHtml + "</tbody></table></div>";
      }

      for (let index = 0; index < lines.length; index += 1) {
        const line = lines[index];
        const nextLine = lines[index + 1] || "";
        const fence = line.match(/^\`\`\`\\s*([\\w-]+)?\\s*$/);
        if (fence) {
          flushParagraph();
          flushList();
          if (inCode) {
            flushCode();
          } else {
            inCode = true;
            codeLines = [];
            codeLanguage = fence[1] || "";
          }
          continue;
        }
        if (inCode) {
          codeLines.push(line);
          continue;
        }
        if (!line.trim()) {
          flushParagraph();
          flushList();
          continue;
        }
        if (line.includes("|") && isTableDivider(nextLine)) {
          flushParagraph();
          flushList();
          const headerCells = parseTableRow(line);
          const rows = [];
          index += 2;
          while (index < lines.length && lines[index].trim() && lines[index].includes("|")) {
            rows.push(parseTableRow(lines[index]));
            index += 1;
          }
          index -= 1;
          output.push(renderTable(headerCells, rows));
          continue;
        }
        if (isHorizontalRule(line)) {
          flushParagraph();
          flushList();
          output.push("<hr>");
          continue;
        }
        const heading = line.match(/^(#{1,6})\\s+(.*)$/);
        if (heading) {
          flushParagraph();
          flushList();
          const level = heading[1].length;
          const anchorId = slugifyHeading(heading[2], headingIds);
          output.push("<h" + level + " id=\\"" + escapeHtml(anchorId) + "\\">" + renderInline(heading[2]) + "</h" + level + ">");
          continue;
        }
        const quote = line.match(/^>\\s?(.*)$/);
        if (quote) {
          flushParagraph();
          flushList();
          output.push("<blockquote><p>" + renderInline(quote[1]) + "</p></blockquote>");
          continue;
        }
        const unordered = line.match(/^[-*]\\s+(.*)$/);
        if (unordered) {
          flushParagraph();
          if (listType && listType !== "ul") {
            flushList();
          }
          listType = "ul";
          listItems.push("<li>" + renderInline(unordered[1]) + "</li>");
          continue;
        }
        const ordered = line.match(/^\\d+\\.\\s+(.*)$/);
        if (ordered) {
          flushParagraph();
          if (listType && listType !== "ol") {
            flushList();
          }
          listType = "ol";
          listItems.push("<li>" + renderInline(ordered[1]) + "</li>");
          continue;
        }
        paragraph.push(line.trim());
      }

      flushParagraph();
      flushList();
      flushCode();
      return output.join("\\n");
    }

    function renderContentFrame(bodyHtml) {
      return '<div class="content-shell"><div class="file-meta">' + escapeHtml(relativePath) + '</div><div class="markdown-body">' + bodyHtml + '</div></div>';
    }

    function setSidebarCollapsed(collapsed) {
      document.body.classList.toggle("sidebar-collapsed", Boolean(collapsed));
      if (sidebarToggle) {
        sidebarToggle.textContent = collapsed ? "▶" : "◀";
        sidebarToggle.setAttribute("aria-label", collapsed ? "Expand file tree" : "Collapse file tree");
        sidebarToggle.setAttribute("title", collapsed ? "Expand file tree" : "Collapse file tree");
      }
      try {
        window.localStorage.setItem(sidebarStateKey, collapsed ? "1" : "0");
      } catch {}
    }

    function restoreSidebarState() {
      try {
        return window.localStorage.getItem(sidebarStateKey) === "1";
      } catch {
        return false;
      }
    }

    function captureOpenFolders() {
      openFolders.clear();
      document.querySelectorAll("details[data-path]").forEach((details) => {
        if (details.open) {
          openFolders.add(details.dataset.path);
        }
      });
    }

    function renderTreeItems(items) {
      return "<ul class=\\"tree\\">" + items.map((item) => {
        if (item.children && item.children.length) {
          const shouldOpen = (item.path && relativePath.startsWith(item.path + "/")) || openFolders.has(item.path);
          return "<li><details data-path=\\"" + escapeHtml(item.path || "") + "\\" " + (shouldOpen ? "open" : "") + "><summary>" + escapeHtml(item.title) + "</summary>" + renderTreeItems(item.children) + "</details></li>";
        }
        const active = item.sourcePath === relativePath ? " active" : "";
        const href = item.kind === "markdown"
          ? bootstrapHref(item.sourcePath || "")
          : rawFileHref(item.sourcePath || "");
        return "<li><a class=\\"repo-link" + active + "\\" href=\\"" + escapeHtml(href) + "\\">" + escapeHtml(item.title) + "</a></li>";
      }).join("") + "</ul>";
    }

    async function loadTree() {
      captureOpenFolders();
      const response = await fetch("/__workspace_doc_browser__/tree", { cache: "no-store" });
      if (!response.ok) {
        throw new Error("HTTP " + response.status);
      }
      const tree = await response.json();
      const treeJson = JSON.stringify(tree);
      if (treeJson !== lastTreeJson) {
        lastTreeJson = treeJson;
        sidebarBody.innerHTML = renderTreeItems(tree);
      }
    }

    async function loadCurrentMarkdown() {
      const response = await fetch("/" + encodePath(relativePath), { cache: "no-store" });
      if (!response.ok) {
        throw new Error("HTTP " + response.status);
      }
      const text = await response.text();
      if (text !== lastMarkdown) {
        lastMarkdown = text;
        content.innerHTML = renderContentFrame(renderMarkdown(text));
        await renderMermaidDiagrams();
        if (window.location.hash) {
          const target = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
          if (target) {
            target.scrollIntoView();
          }
        }
      }
    }

    async function refreshTree() {
      try {
        await loadTree();
      } catch {}
    }

    async function refreshMarkdown() {
      try {
        await loadCurrentMarkdown();
      } catch (error) {
        content.innerHTML = renderContentFrame('<p class="error-state">Unable to load markdown preview.</p><pre><code>' + escapeHtml(String(error)) + '</code></pre>');
      }
    }

    document.title = relativePath ? relativePath + " - " + workspaceName : workspaceName;
    if (sidebarToggle) {
      sidebarToggle.addEventListener("click", () => {
        setSidebarCollapsed(!document.body.classList.contains("sidebar-collapsed"));
      });
    }
    setSidebarCollapsed(restoreSidebarState());
    refreshTree();
    refreshMarkdown();
    setInterval(refreshTree, treeRefreshMs);
    setInterval(refreshMarkdown, fileRefreshMs);
  </script>
</body>
</html>`;
}

function waitForPortReady(port, attempts = 40, delayMs = 150) {
  return new Promise((resolve, reject) => {
    let remaining = attempts;

    const tryConnect = () => {
      const socket = net.createConnection({ port, host: "127.0.0.1" });
      socket.once("connect", () => {
        socket.destroy();
        resolve();
      });
      socket.once("error", () => {
        socket.destroy();
        remaining -= 1;
        if (remaining <= 0) {
          reject(new Error(`Timed out waiting for local docs server on port ${port}`));
        } else {
          setTimeout(tryConnect, delayMs);
        }
      });
    };

    tryConnect();
  });
}

function findFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = address && typeof address === "object" ? address.port : null;
      server.close((error) => {
        if (error) {
          reject(error);
        } else if (port) {
          resolve(port);
        } else {
          reject(new Error("Failed to allocate a local preview port."));
        }
      });
    });
  });
}

function activate(context) {
  const browser = new WorkspaceDocBrowser(context);
  browser.activate();
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
