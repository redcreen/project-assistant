"use strict";

const cp = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const net = require("net");
const vscode = require("vscode");

const COMMAND_ID = "redcreen.workspaceDocBrowser.open";
const OUTPUT_NAME = "Workspace Doc Browser";
const BUTTON_TEXT = "$(globe) Browse Docs";
const LIVE_TEXT = "$(globe) Docs Live";
const STARTING_TEXT = "$(sync~spin) Starting Docs";
const REBUILDING_TEXT = "$(sync~spin) Rebuilding Docs";
const DOCS_STARTUP_LOG_REVEAL_MS = 2500;
const DOCS_STARTUP_READY_ATTEMPTS = 240;
const DOCS_STARTUP_READY_DELAY_MS = 250;
const DOCS_REBUILD_DEBOUNCE_MS = 600;

class WorkspaceDocBrowser {
  constructor(context) {
    this.context = context;
    this.output = vscode.window.createOutputChannel(OUTPUT_NAME);
    this.statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 90);
    this.session = null;
    this.pendingOpen = null;
    this.rebuildTimer = null;
  }

  activate() {
    const watcher = vscode.workspace.createFileSystemWatcher("**/*.md");
    this.context.subscriptions.push(
      this.output,
      this.statusBar,
      watcher,
      vscode.commands.registerCommand(COMMAND_ID, (targetUri) => this.open(targetUri)),
      vscode.workspace.onDidChangeWorkspaceFolders(() => this.updateStatusBar()),
      vscode.window.onDidChangeActiveTextEditor(() => this.updateStatusBar()),
      watcher.onDidChange((uri) => this.handleMarkdownMutation(uri, "changed")),
      watcher.onDidCreate((uri) => this.handleMarkdownMutation(uri, "created")),
      watcher.onDidDelete((uri) => this.handleMarkdownMutation(uri, "deleted")),
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

  getPreferredStartUrl(baseUrl, workspaceRoot, targetUri) {
    const normalizedTargetUri = this.normalizeTargetUri(targetUri);
    if (!normalizedTargetUri) {
      return baseUrl;
    }
    const activePath = normalizedTargetUri.fsPath;
    const relativePath = path.relative(workspaceRoot, activePath);
    if (!relativePath || relativePath.startsWith("..") || path.isAbsolute(relativePath)) {
      return baseUrl;
    }
    if (!/\.md$/i.test(activePath)) {
      return baseUrl;
    }
    const normalizedRelativePath = normalizeSlashes(relativePath);
    if (markdownPathNeedsRawView(normalizedRelativePath)) {
      const preferredUrl = new URL(baseUrl);
      preferredUrl.searchParams.set("view", normalizedRelativePath);
      return preferredUrl.toString();
    }
    const href = markdownPathToHref(normalizedRelativePath);
    return new URL(href, baseUrl).toString();
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
      ? (this.pendingOpen.kind === "rebuild" ? REBUILDING_TEXT : STARTING_TEXT)
      : (isLive ? LIVE_TEXT : BUTTON_TEXT);
    this.statusBar.tooltip = isPending
      ? this.pendingOpen.detail
      : isLive
        ? `Open the live browser preview for ${path.basename(workspaceRoot)}`
        : `Open ${path.basename(workspaceRoot)} in a browser as rendered Markdown`;
    this.statusBar.command = COMMAND_ID;
    this.statusBar.show();
  }

  setPendingOpen(workspaceRoot, detail, kind = "start") {
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
    if (this.session && this.session.rebuildRequested && this.isSessionAlive(this.session)) {
      const { targetUri } = this.session;
      this.session.rebuildRequested = false;
      this.scheduleSessionRebuild(targetUri, this.session.workspaceRoot, "queued changes after the previous rebuild");
    }
  }

  async openExternalUrl(url, workspaceRoot, contextLabel, session) {
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

  async openLiveSession(session, workspaceRoot, targetUri) {
    if (!session || !this.isSessionAlive(session)) {
      return false;
    }
    return this.startSession({
      targetUri,
      workspaceRoot,
      detail: `Rebuilding live docs preview for ${path.basename(workspaceRoot)}…`,
      kind: "rebuild",
      port: session.port,
      rawPort: session.rawPort,
      openInBrowser: true,
    });
  }

  async open(targetUri) {
    const workspaceRoot = this.getWorkspaceRoot(targetUri);
    if (!workspaceRoot) {
      vscode.window.showWarningMessage("Workspace Doc Browser: open a local folder first.");
      return;
    }

    if (this.session && this.session.workspaceRoot === workspaceRoot && this.isSessionAlive(this.session)) {
      await this.openLiveSession(this.session, workspaceRoot, targetUri);
      return;
    }

    await this.startSession({
      targetUri,
      workspaceRoot,
      detail: `Starting local docs preview for ${path.basename(workspaceRoot)}…`,
      kind: "start",
      openInBrowser: true,
    });
  }

  async startSession(options) {
    const {
      targetUri,
      workspaceRoot,
      detail,
      kind,
      port: preferredPort,
      rawPort: preferredRawPort,
      openInBrowser,
    } = options;

    this.setPendingOpen(workspaceRoot, detail, kind);

    const previousSession = this.session && this.session.workspaceRoot === workspaceRoot ? this.session : null;
    const port = preferredPort || await findFreePort();
    const rawPort = preferredRawPort || await findFreePort();

    this.disposeSession();

    const rawServerBase = `http://127.0.0.1:${rawPort}`;
    const { configPath, siteDir } = ensureMkDocsConfig(workspaceRoot, { rawServerBase });
    const url = `http://127.0.0.1:${port}/`;
    const preferredUrl = this.getPreferredStartUrl(url, workspaceRoot, targetUri);
    const shell = process.env.SHELL || "/bin/zsh";
    const command = `mkdocs serve -f ${shellQuote(configPath)} -a 127.0.0.1:${port}`;
    const rawServerScript = buildRawFileServerScript(workspaceRoot, rawPort);
    const rawProcess = cp.spawn(process.execPath, ["-e", rawServerScript], {
      cwd: workspaceRoot,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });
    const child = cp.spawn(shell, ["-lc", command], {
      cwd: workspaceRoot,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });

    const session = {
      workspaceRoot,
      targetUri: this.normalizeTargetUri(targetUri),
      url,
      preferredUrl,
      port,
      rawPort,
      browserOpened: previousSession ? previousSession.browserOpened : false,
      rebuildRequested: false,
      process: child,
      rawProcess,
      rawServerBase,
      configPath,
      siteDir,
    };
    this.session = session;
    this.updateStatusBar();
    this.output.appendLine(`[${kind}] ${workspaceRoot}`);
    this.output.appendLine(`[cmd] ${command}`);
    this.output.appendLine(`[open] ${preferredUrl}`);
    this.output.appendLine(`[raw] ${rawServerBase}`);

    waitForPortReady(port, DOCS_STARTUP_READY_ATTEMPTS, DOCS_STARTUP_READY_DELAY_MS).then(() => {
      if (this.session !== session) {
        return null;
      }
      this.clearPendingOpen();
      session.browserOpened = Boolean(previousSession && previousSession.browserOpened);
      if (openInBrowser) {
        return this.openExternalUrl(preferredUrl, workspaceRoot, "the docs preview", session);
      }
      this.updateStatusBar();
      this.output.appendLine(`[ready] ${preferredUrl}`);
      return null;
    }).catch((error) => {
      this.clearPendingOpen();
      this.output.appendLine(`[open-error] ${String(error)}`);
      this.output.show(true);
      vscode.window.showWarningMessage(
        `Workspace Doc Browser: the docs server for ${path.basename(workspaceRoot)} did not become ready yet. Check the Workspace Doc Browser output for details.`,
      );
    });

    child.stdout.on("data", (chunk) => {
      this.output.append(chunk.toString());
    });
    child.stderr.on("data", (chunk) => {
      this.output.append(chunk.toString());
    });
    child.on("error", (error) => {
      this.clearPendingOpen();
      this.output.appendLine(`[error] ${String(error)}`);
      vscode.window.showErrorMessage(`Workspace Doc Browser: ${String(error)}`);
      if (this.session === session) {
        this.session = null;
        this.updateStatusBar();
      }
    });
    child.on("exit", (code, signal) => {
      this.clearPendingOpen();
      this.output.appendLine(`[exit] code=${code} signal=${signal}`);
      const wasCurrentSession = this.session === session;
      if (wasCurrentSession) {
        this.session = null;
        this.updateStatusBar();
      }
      if (code && code !== 0) {
        const message = code === 127
          ? "MkDocs was not found in the VS Code shell environment."
          : `MkDocs preview exited with code ${code}.`;
        vscode.window.showErrorMessage(`Workspace Doc Browser: ${message}`);
        this.output.show(true);
      } else if (wasCurrentSession && signal !== "SIGTERM") {
        vscode.window.showWarningMessage("Workspace Doc Browser: preview stopped.");
      }
    });

    rawProcess.stdout.on("data", (chunk) => {
      this.output.append(chunk.toString());
    });
    rawProcess.stderr.on("data", (chunk) => {
      this.output.append(chunk.toString());
    });
    rawProcess.on("error", (error) => {
      this.output.appendLine(`[raw-error] ${String(error)}`);
    });
    rawProcess.on("exit", (code, signal) => {
      this.output.appendLine(`[raw-exit] code=${code} signal=${signal}`);
    });
    return true;
  }

  handleMarkdownMutation(targetUri, eventType) {
    if (!targetUri || targetUri.scheme !== "file" || !/\.md$/i.test(targetUri.fsPath)) {
      return;
    }
    const workspaceRoot = this.getWorkspaceRoot(targetUri);
    if (!workspaceRoot || !this.session || this.session.workspaceRoot !== workspaceRoot || !this.isSessionAlive(this.session)) {
      return;
    }
    this.session.dirty = true;
    this.session.rebuildRequested = true;
    this.session.targetUri = this.normalizeTargetUri(targetUri) || this.session.targetUri;
    this.output.appendLine(`[content-${eventType}] ${normalizeSlashes(path.relative(workspaceRoot, targetUri.fsPath))}`);
    this.scheduleSessionRebuild(targetUri, workspaceRoot, `${eventType} markdown content`);
  }

  scheduleSessionRebuild(targetUri, workspaceRoot, reason) {
    if (this.rebuildTimer) {
      clearTimeout(this.rebuildTimer);
    }
    this.rebuildTimer = setTimeout(() => {
      this.rebuildTimer = null;
      if (!this.session || this.session.workspaceRoot !== workspaceRoot || !this.isSessionAlive(this.session)) {
        return;
      }
      if (this.pendingOpen && this.pendingOpen.workspaceRoot === workspaceRoot) {
        this.session.rebuildRequested = true;
        return;
      }
      this.session.rebuildRequested = false;
      this.startSession({
        targetUri: targetUri || this.session.targetUri,
        workspaceRoot,
        detail: `Rebuilding docs preview for ${path.basename(workspaceRoot)} after ${reason}…`,
        kind: "rebuild",
        port: this.session.port,
        rawPort: this.session.rawPort,
        openInBrowser: false,
      }).catch((error) => {
        this.output.appendLine(`[rebuild-error] ${String(error)}`);
      });
    }, DOCS_REBUILD_DEBOUNCE_MS);
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
    if (this.rebuildTimer) {
      clearTimeout(this.rebuildTimer);
      this.rebuildTimer = null;
    }
    if (!this.session) {
      return;
    }
    const { process: child, rawProcess } = this.session;
    this.session = null;
    if (child && !child.killed) {
      try {
        child.kill("SIGTERM");
      } catch {}
    }
    if (rawProcess && !rawProcess.killed) {
      try {
        rawProcess.kill("SIGTERM");
      } catch {}
    }
  }
}

function ensureMkDocsConfig(workspaceRoot, options = {}) {
  const safeName = `${path.basename(workspaceRoot) || "workspace"}-${Buffer.from(workspaceRoot).toString("base64").replace(/[^a-zA-Z0-9]/g, "").slice(0, 12)}`;
  const baseDir = path.join(os.tmpdir(), "workspace-doc-browser", safeName);
  const siteDir = path.join(baseDir, "site");
  const configPath = path.join(baseDir, "mkdocs.yml");
  const themeDir = path.join(baseDir, "theme");
  fs.mkdirSync(baseDir, { recursive: true });
  fs.mkdirSync(themeDir, { recursive: true });
  fs.writeFileSync(path.join(themeDir, "main.html"), buildGithubLikeMainTemplate(), "utf8");
  const nav = buildWorkspaceNav(workspaceRoot);
  const repoTree = buildRepoTree(workspaceRoot, "", options.rawServerBase || "");
  const config = [
    `site_name: ${yamlString(path.basename(workspaceRoot) || "Workspace Docs")}`,
    `docs_dir: ${yamlString(workspaceRoot)}`,
    `site_dir: ${yamlString(siteDir)}`,
    "strict: false",
    "use_directory_urls: false",
    "theme:",
    "  name: mkdocs",
    `  custom_dir: ${yamlString(themeDir)}`,
    "exclude_docs: |",
    "  .git/",
    "  .vscode/",
    "  .idea/",
    "  node_modules/",
    "  .DS_Store",
    "",
    "extra:",
    `  workspace_name: ${yamlString(path.basename(workspaceRoot) || "Workspace Docs")}`,
    `  raw_server_base: ${yamlString(options.rawServerBase || "")}`,
    "  repo_tree:",
    renderRepoTreeYaml(repoTree, 4),
    "",
    "nav:",
    renderNavYaml(nav, 2),
  ].join("\n");
  fs.writeFileSync(configPath, config, "utf8");
  return { configPath, siteDir };
}

function buildWorkspaceNav(workspaceRoot) {
  const tree = buildMarkdownTree(workspaceRoot, "");
  const homepage = tree.files.find((item) => /^readme(\.[^.]+)?\.md$/i.test(item.title) || /^index\.md$/i.test(item.title));
  const items = [];
  if (homepage) {
    items.push(homepage);
  }
  for (const dir of tree.directories) {
    items.push(dir);
  }
  for (const file of tree.files) {
    if (file !== homepage) {
      items.push(file);
    }
  }
  return items;
}

function buildMarkdownTree(workspaceRoot, relativeDir) {
  const absoluteDir = path.join(workspaceRoot, relativeDir);
  const entries = fs.readdirSync(absoluteDir, { withFileTypes: true })
    .filter((entry) => !shouldIgnoreEntry(entry.name, entry.isDirectory(), { includeDotfiles: false }))
    .sort(compareEntries);

  const directories = [];
  const files = [];

  for (const entry of entries) {
    const relativePath = normalizeSlashes(path.posix.join(relativeDir, entry.name));
    const absolutePath = path.join(workspaceRoot, relativePath);
    if (entry.isDirectory()) {
      const child = buildMarkdownTree(workspaceRoot, relativePath);
      if (child.directories.length || child.files.length) {
        directories.push({
          title: `${entry.name}/`,
          children: [...child.directories, ...child.files],
        });
      }
      continue;
    }
    if (entry.isFile() && isMarkdownFile(entry.name, absolutePath)) {
      files.push({
        title: entry.name,
        path: relativePath,
      });
    }
  }

  return {
    directories,
    files,
  };
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
    return ["node_modules", ".git", ".vscode", ".idea", "__pycache__", ".mkdocs", ".mkdocs-site"].includes(name);
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

function normalizeSlashes(value) {
  return String(value || "").replace(/\\/g, "/");
}

function encodePathSegments(value) {
  return normalizeSlashes(String(value || ""))
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/");
}

function markdownPathToHref(relativePath) {
  const normalized = normalizeSlashes(String(relativePath || ""));
  const base = path.posix.basename(normalized).toLowerCase();
  if (base === "readme.md" || base === "index.md") {
    const dir = path.posix.dirname(normalized);
    return !dir || dir === "." ? "index.html" : `${dir}/index.html`;
  }
  return normalized.replace(/\.md$/i, ".html");
}

function markdownPathNeedsRawView(relativePath) {
  const normalized = normalizeSlashes(String(relativePath || ""));
  if (!normalized) {
    return false;
  }
  return normalized
    .split("/")
    .some((segment) => segment.startsWith(".") && segment !== ".github");
}

function buildRepoTree(workspaceRoot, relativeDir, rawServerBase = "") {
  const absoluteDir = path.join(workspaceRoot, relativeDir);
  const entries = fs.readdirSync(absoluteDir, { withFileTypes: true })
    .filter((entry) => !shouldIgnoreEntry(entry.name, entry.isDirectory(), { includeDotfiles: true }))
    .sort(compareEntries);

  const items = [];

  for (const entry of entries) {
    const relativePath = normalizeSlashes(path.posix.join(relativeDir, entry.name));
    const absolutePath = path.join(workspaceRoot, relativePath);
    if (entry.isDirectory()) {
      items.push({
        title: `${entry.name}/`,
        kind: "directory",
        path: relativePath,
        children: buildRepoTree(workspaceRoot, relativePath, rawServerBase),
      });
      continue;
    }
    if (!entry.isFile()) {
      continue;
    }
    const markdown = isMarkdownFile(entry.name, absolutePath);
    const markdownUsesRawView = markdown && markdownPathNeedsRawView(relativePath);
    items.push({
      title: entry.name,
      kind: markdown ? "markdown" : "file",
      href: markdown
        ? (markdownUsesRawView ? `?view=${encodeURIComponent(relativePath)}` : markdownPathToHref(relativePath))
        : `${String(rawServerBase || "").replace(/\/$/, "")}/${encodePathSegments(relativePath)}`,
      sourcePath: relativePath,
      viewPath: markdownUsesRawView || !markdown ? relativePath : "",
    });
  }

  return items;
}

function renderNavYaml(items, indent = 0) {
  const lines = [];
  const spaces = " ".repeat(indent);
  for (const item of items) {
    if (item.children) {
      lines.push(`${spaces}- ${yamlString(item.title)}:`);
      lines.push(renderNavYaml(item.children, indent + 2));
    } else {
      lines.push(`${spaces}- ${yamlString(item.title)}: ${yamlString(item.path)}`);
    }
  }
  return lines.filter(Boolean).join("\n");
}

function renderRepoTreeYaml(items, indent = 0) {
  const lines = [];
  const spaces = " ".repeat(indent);
  for (const item of items) {
    lines.push(`${spaces}- title: ${yamlString(item.title)}`);
    lines.push(`${spaces}  kind: ${yamlString(item.kind)}`);
    if (item.path) {
      lines.push(`${spaces}  path: ${yamlString(item.path)}`);
    }
    if (item.href) {
      lines.push(`${spaces}  href: ${yamlString(item.href)}`);
    }
    if (item.sourcePath) {
      lines.push(`${spaces}  source_path: ${yamlString(item.sourcePath)}`);
    }
    if (item.viewPath) {
      lines.push(`${spaces}  view_path: ${yamlString(item.viewPath)}`);
    }
    if (item.children && item.children.length) {
      lines.push(`${spaces}  children:`);
      lines.push(renderRepoTreeYaml(item.children, indent + 4));
    }
  }
  return lines.filter(Boolean).join("\n");
}

function buildRawFileServerScript(workspaceRoot, port) {
  return `
const http = require("http");
const fs = require("fs");
const path = require("path");
const root = ${JSON.stringify(workspaceRoot)};
const port = ${Number(port)};

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
    "Cache-Control": "no-store"
  });
  res.end(body);
}

http.createServer((req, res) => {
  if (!req.url) {
    return send(res, 400, "Bad Request", "text/plain; charset=utf-8");
  }
  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "*"
    });
    return res.end();
  }
  const parsed = new URL(req.url, "http://127.0.0.1");
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

function buildGithubLikeMainTemplate() {
  return `{% extends "base.html" %}
{% macro render_tree(items, depth=0) -%}
  <ul class="repo-tree level-{{ depth }}">
    {%- for item in items %}
      {%- set is_current_markdown = page and page.file and item.source_path and item.source_path == page.file.src_path %}
      {%- set is_open_markdown_dir = page and page.file and item.path and page.file.src_path.startswith(item.path + '/') %}
      <li class="repo-node{% if is_current_markdown %} active{% endif %}{% if item.children %} is-directory{% else %} is-file{% endif %}" data-depth="{{ depth }}">
        {%- if item.children %}
          <details class="repo-folder"{% if is_open_markdown_dir %} open{% endif %}>
            <summary class="repo-folder-label">{{ item.title }}</summary>
            {{ render_tree(item.children, depth + 1) }}
          </details>
        {%- else %}
          <a class="repo-link{% if is_current_markdown %} active{% endif %}" data-source-path="{{ item.source_path|default('') }}" data-view-path="{{ item.view_path|default('') }}" href="{{ item.href|url }}">{{ item.title }}</a>
        {%- endif %}
      </li>
    {%- endfor %}
  </ul>
{%- endmacro %}
{% block extrahead %}
  {{ super() }}
  <style>
    :root {
      --gh-canvas-default: #ffffff;
      --gh-canvas-subtle: #f6f8fa;
      --gh-border-default: #d0d7de;
      --gh-border-muted: #d8dee4;
      --gh-fg-default: #1f2328;
      --gh-fg-muted: #59636e;
      --gh-accent-fg: #0969da;
      --gh-accent-emphasis: #0550ae;
      --gh-code-bg: rgba(175, 184, 193, 0.2);
      --gh-pre-bg: #f6f8fa;
      --gh-heading-border: #d8dee4;
      --gh-blockquote: #d0d7de;
      --gh-table-header: #f6f8fa;
      --gh-shadow: 0 1px 0 rgba(31, 35, 40, 0.04);
      --gh-sidebar-width: 252px;
    }

    html, body {
      background: var(--gh-canvas-subtle);
      color: var(--gh-fg-default);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 14px;
      line-height: 1.5;
    }

    body {
      min-height: 100vh;
    }

    .navbar {
      background: var(--gh-canvas-default);
      border-bottom: 1px solid var(--gh-border-default);
      box-shadow: var(--gh-shadow);
      min-height: 56px;
      margin-bottom: 20px;
    }

    .navbar .navbar-brand,
    .navbar .navbar-nav > li > a {
      color: var(--gh-fg-default) !important;
      font-weight: 600;
    }

    .navbar .navbar-nav > li > a:hover,
    .navbar .navbar-brand:hover {
      color: var(--gh-accent-fg) !important;
      background: transparent;
    }

    .container {
      width: min(100%, 1360px);
    }

    .navbar .nav.navbar-nav {
      display: none !important;
    }

    .workspace-layout {
      display: grid;
      grid-template-columns: var(--gh-sidebar-width) minmax(0, 1fr);
      gap: 24px;
      align-items: start;
      margin-bottom: 32px;
    }

    .repo-sidebar {
      position: sticky;
      top: 76px;
      max-height: calc(100vh - 92px);
      background: var(--gh-canvas-default);
      border: 1px solid var(--gh-border-default);
      border-radius: 6px;
      box-shadow: var(--gh-shadow);
      overflow: hidden;
    }

    .repo-sidebar,
    .repo-tree-wrap {
      scrollbar-width: thin;
    }

    .repo-sidebar-header {
      padding: 12px 14px;
      font-size: 14px;
      font-weight: 700;
      border-bottom: 1px solid var(--gh-border-muted);
      background: linear-gradient(to bottom, #ffffff, #fafbfc);
    }

    .repo-tree-wrap {
      max-height: calc(100vh - 146px);
      overflow: auto;
      padding: 8px 0;
    }

    .repo-tree {
      margin: 0;
      padding: 0;
      list-style: none;
    }

    .repo-tree,
    .repo-tree ul,
    .repo-tree li,
    .repo-folder,
    details.repo-folder,
    details.repo-folder[open] {
      background: transparent !important;
      border: 0 !important;
      box-shadow: none !important;
      min-height: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
    }

    .repo-tree ul {
      margin-bottom: 0 !important;
      padding-top: 0 !important;
      padding-bottom: 0 !important;
    }

    .repo-tree .repo-tree {
      padding-left: 12px;
      margin-top: 0;
    }

    .repo-folder > .repo-tree {
      margin-left: 14px !important;
      padding-left: 10px !important;
      border-left: 1px solid rgba(208, 215, 222, 0.9) !important;
    }

    .repo-node {
      list-style: none;
    }

    .repo-folder summary {
      list-style: none;
      display: block;
    }

    .repo-folder summary::-webkit-details-marker {
      display: none;
    }

    .repo-folder-label,
    .repo-link {
      display: block;
      position: relative;
      padding: 4px 10px 4px 28px !important;
      color: var(--gh-fg-muted);
      font-size: 12px;
      line-height: 1.35;
      text-decoration: none;
      border-radius: 4px;
      margin: 0 6px !important;
      cursor: pointer;
    }

    .repo-folder-label {
      font-weight: 600;
      color: var(--gh-fg-default);
    }

    .repo-folder-label::before {
      content: "▸";
      position: absolute;
      left: 8px;
      top: 4px;
      font-size: 10px;
      color: var(--gh-fg-muted);
      transition: transform 120ms ease;
    }

    .repo-folder[open] > .repo-folder-label::before {
      transform: rotate(90deg);
    }

    .repo-folder-label::after {
      content: "";
      position: absolute;
      left: 20px;
      top: 5px;
      width: 11px;
      height: 9px;
      border: 1px solid #bf8700;
      border-radius: 2px 2px 1px 1px;
      background: linear-gradient(to bottom, #fff8c5, #f8e3a1);
      box-sizing: border-box;
      opacity: 0.95;
    }

    .repo-link::before {
      content: "";
      position: absolute;
      left: 8px;
      top: 4px;
      width: 10px;
      height: 12px;
      border: 1px solid var(--gh-border-default);
      border-radius: 2px;
      background: linear-gradient(to bottom, #ffffff, #f6f8fa);
      box-sizing: border-box;
      opacity: 0.9;
    }

    .repo-folder-label,
    .repo-link {
      padding-left: 24px !important;
    }

    .repo-folder-label {
      padding-left: 36px !important;
    }

    .repo-folder-label:hover,
    .repo-link:hover {
      color: var(--gh-accent-fg);
      background: rgba(9, 105, 218, 0.06);
      text-decoration: none;
    }

    .repo-node.active > .repo-link,
    .repo-node.active > .repo-folder > .repo-folder-label,
    .repo-link.active {
      color: var(--gh-accent-emphasis);
      background: rgba(9, 105, 218, 0.08);
      font-weight: 600;
    }

    .repo-node.is-directory {
      margin-bottom: 1px;
    }

    .repo-link.active::before {
      border-color: rgba(9, 105, 218, 0.35);
      background: rgba(9, 105, 218, 0.08);
    }

    .repo-content {
      min-width: 0;
    }

    .repo-page-header {
      margin-bottom: 12px;
      padding: 14px 16px;
      background: var(--gh-canvas-default);
      border: 1px solid var(--gh-border-default);
      border-radius: 6px;
      box-shadow: var(--gh-shadow);
    }

    .repo-page-title {
      font-size: 22px;
      font-weight: 700;
      line-height: 1.3;
      color: var(--gh-fg-default);
    }

    .repo-page-subtitle {
      margin-top: 4px;
      color: var(--gh-fg-muted);
      font-size: 13px;
    }

    .repo-breadcrumb {
      margin-bottom: 12px;
      font-size: 14px;
      font-weight: 600;
      color: var(--gh-fg-muted);
    }

    .repo-breadcrumb .current {
      color: var(--gh-fg-default);
    }

    .markdown-body {
      padding: 32px 40px;
      background: var(--gh-canvas-default);
      border: 1px solid var(--gh-border-default);
      border-radius: 6px;
      box-shadow: var(--gh-shadow);
    }

    @media (max-width: 900px) {
      .workspace-layout {
        grid-template-columns: 1fr;
      }

      .repo-sidebar {
        position: static;
        max-height: none;
        margin-bottom: 16px;
      }

      .repo-tree-wrap {
        max-height: none;
      }

      .markdown-body {
        padding: 24px 20px;
        border-left: 0;
        border-right: 0;
        border-radius: 0;
      }
    }

    .markdown-body > h1:first-child,
    .markdown-body > h2:first-child,
    .markdown-body > h3:first-child {
      margin-top: 0;
      padding-top: 0;
    }

    .markdown-body h1,
    .markdown-body h2,
    .markdown-body h3,
    .markdown-body h4,
    .markdown-body h5,
    .markdown-body h6 {
      color: var(--gh-fg-default);
      font-weight: 600;
      line-height: 1.25;
      margin-top: 24px;
      margin-bottom: 16px;
    }

    .markdown-body h1,
    .markdown-body h2 {
      padding-bottom: 0.3em;
      border-bottom: 1px solid var(--gh-heading-border);
    }

    .markdown-body h1 { font-size: 2em; }
    .markdown-body h2 { font-size: 1.5em; }
    .markdown-body h3 { font-size: 1.25em; }
    .markdown-body h4 { font-size: 1em; }
    .markdown-body h5 { font-size: 0.875em; }
    .markdown-body h6 { font-size: 0.85em; color: var(--gh-fg-muted); }

    .markdown-body p,
    .markdown-body ul,
    .markdown-body ol,
    .markdown-body dl,
    .markdown-body table,
    .markdown-body blockquote,
    .markdown-body pre {
      margin-top: 0;
      margin-bottom: 16px;
    }

    .markdown-body a {
      color: var(--gh-accent-fg);
      text-decoration: none;
    }

    .markdown-body a:hover {
      color: var(--gh-accent-emphasis);
      text-decoration: underline;
    }

    .markdown-body code,
    .markdown-body tt {
      padding: 0.2em 0.4em;
      margin: 0;
      font-size: 85%;
      white-space: break-spaces;
      background: var(--gh-code-bg);
      border-radius: 6px;
      font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, "Liberation Mono", monospace;
    }

    .markdown-body pre {
      padding: 16px;
      overflow: auto;
      font-size: 85%;
      line-height: 1.45;
      background: var(--gh-pre-bg);
      border-radius: 6px;
      border: 1px solid var(--gh-border-muted);
    }

    .markdown-body pre code {
      padding: 0;
      background: transparent;
      border-radius: 0;
      white-space: pre;
    }

    .repo-code-view {
      margin: 0;
      white-space: pre;
    }

    .repo-file-meta {
      margin-bottom: 12px;
      color: var(--gh-fg-muted);
      font-size: 12px;
    }

    .markdown-body blockquote {
      padding: 0 1em;
      color: var(--gh-fg-muted);
      border-left: 0.25em solid var(--gh-blockquote);
    }

    .markdown-body hr {
      height: 0.25em;
      padding: 0;
      margin: 24px 0;
      background: var(--gh-heading-border);
      border: 0;
    }

    .markdown-body table {
      display: block;
      width: max-content;
      max-width: 100%;
      overflow: auto;
      border-spacing: 0;
      border-collapse: collapse;
    }

    .markdown-body table th,
    .markdown-body table td {
      padding: 6px 13px;
      border: 1px solid var(--gh-border-default);
    }

    .markdown-body table th {
      font-weight: 600;
      background: var(--gh-table-header);
    }

    .markdown-body table tr:nth-child(2n) {
      background: var(--gh-canvas-subtle);
    }

    .markdown-body img {
      max-width: 100%;
      height: auto;
      box-sizing: content-box;
      background: var(--gh-canvas-default);
      border-radius: 6px;
    }

    .admonition,
    .alert {
      border: 1px solid var(--gh-border-default);
      border-radius: 6px;
      background: var(--gh-canvas-subtle);
      box-shadow: none;
    }

    .admonition-title,
    .alert-title {
      background: transparent;
      color: var(--gh-fg-default);
      border-bottom: 1px solid var(--gh-border-muted);
      font-weight: 600;
    }

    .navbar .navbar-brand::before {
      content: "Local Docs";
    }

    .navbar .navbar-brand {
      font-size: 0;
    }
  </style>
  <script>
    document.addEventListener("DOMContentLoaded", function () {
      var params = new URLSearchParams(window.location.search);
      var currentView = params.get("view");
      var currentPath = normalizePagePath(window.location.pathname || "/");
      var rawServerBase = {{ config.extra.raw_server_base|tojson }};
      var activeApplied = false;

      function markActive(link) {
        activeApplied = true;
        link.classList.add("active");
        var node = link.closest(".repo-node");
        if (node) {
          node.classList.add("active");
        }
        var parent = link.parentElement;
        while (parent) {
          if (parent.tagName === "DETAILS") {
            parent.open = true;
          }
          if (parent.classList && parent.classList.contains("repo-node")) {
            parent.classList.add("active");
          }
          parent = parent.parentElement;
        }
      }

      function clearActiveLinks() {
        document.querySelectorAll(".repo-link.active, .repo-node.active").forEach(function (node) {
          node.classList.remove("active");
        });
      }

      function renderFileView(viewPath, link) {
        currentView = viewPath;
        var content = document.querySelector(".markdown-body");
        var subtitle = document.querySelector(".repo-page-subtitle");
        var breadcrumb = document.querySelector(".repo-breadcrumb .current");
        if (subtitle) {
          subtitle.textContent = viewPath;
        }
        if (breadcrumb) {
          breadcrumb.textContent = viewPath.split("/").pop() || viewPath;
        }
        document.querySelectorAll(".repo-folder").forEach(function (folder) {
          folder.open = false;
        });
        clearActiveLinks();
        if (link) {
          markActive(link);
        }
        var rawUrl = buildRawFileUrl(rawServerBase, viewPath);
        fetch(rawUrl, { cache: "no-store" })
          .then(function (response) {
            if (!response.ok) {
              throw new Error("HTTP " + response.status);
            }
            return response.text();
          })
          .then(function (text) {
            if (!content) {
              return;
            }
            var escaped = text
              .replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;");
            var ext = viewPath.includes(".") ? viewPath.split(".").pop() : "text";
            content.innerHTML =
              '<div class="repo-file-meta">Viewing local file: ' + escapedPath(viewPath) + '</div>' +
              '<pre class="repo-code-view"><code class="language-' + escapedAttr(ext) + '">' + escaped + '</code></pre>';
          })
          .catch(function (error) {
            if (content) {
              content.innerHTML =
                '<div class="repo-file-meta">Unable to open file: ' + escapedPath(viewPath) + '</div>' +
                '<pre class="repo-code-view"><code>' + escapedPath(String(error)) + '</code></pre>';
            }
          });
      }

      document.querySelectorAll(".repo-link").forEach(function (link) {
        try {
          var target = new URL(link.getAttribute("href"), window.location.href);
          var targetView = link.dataset.viewPath || "";
          if (targetView) {
            link.addEventListener("click", function (event) {
              event.preventDefault();
              history.pushState({ view: targetView }, "", window.location.pathname + "?view=" + encodeURIComponent(targetView));
              renderFileView(targetView, link);
            });
          }
          if (currentView && link.dataset.sourcePath === currentView) {
            markActive(link);
            return;
          }
          if (!currentView && normalizePagePath(target.pathname) === currentPath && !target.search) {
            markActive(link);
          }
        } catch (error) {
          console.warn("repo tree activation failed", error);
        }
      });

      if (currentView) {
        var activeLink = document.querySelector('.repo-link[data-source-path="' + cssEscape(currentView) + '"]');
        renderFileView(currentView, activeLink);
      }

      window.addEventListener("popstate", function () {
        var poppedView = new URLSearchParams(window.location.search).get("view");
        if (poppedView) {
          var activeLink = document.querySelector('.repo-link[data-source-path="' + cssEscape(poppedView) + '"]');
          renderFileView(poppedView, activeLink);
        } else {
          window.location.reload();
        }
      });

      function escapedPath(value) {
        return String(value || "")
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;");
      }

      function escapedAttr(value) {
        return String(value || "")
          .replace(/&/g, "")
          .replace(/"/g, "")
          .replace(/'/g, "")
          .replace(/</g, "")
          .replace(/>/g, "");
      }

      function normalizePagePath(value) {
        if (!value || value === "/") {
          return "/";
        }
        return value.replace(/\/index\.html$/i, "/");
      }

      function buildRawFileUrl(base, relativePath) {
        var normalizedBase = String(base || "").replace(/\/$/, "");
        var encodedPath = String(relativePath || "")
          .split("/")
          .map(function (segment) { return encodeURIComponent(segment); })
          .join("/");
        return normalizedBase + "/" + encodedPath;
      }

      function cssEscape(value) {
        if (window.CSS && typeof window.CSS.escape === "function") {
          return window.CSS.escape(String(value || ""));
        }
        return String(value || "").replace(/["\\]/g, "\\$&");
      }
    });
  </script>
{% endblock %}
{% block content %}
  <div class="workspace-layout">
    <aside class="repo-sidebar">
      <div class="repo-sidebar-header">Files</div>
      <div class="repo-tree-wrap">
        {{ render_tree(config.extra.repo_tree) }}
      </div>
    </aside>
    <section class="repo-content" role="main">
      <div class="repo-page-header">
        <div class="repo-page-title">{{ config.extra.workspace_name }}</div>
        <div class="repo-page-subtitle">{{ page.file.src_path if page and page.file else page.title }}</div>
      </div>
      <div class="repo-breadcrumb">{{ config.site_name }} / <span class="current">{{ page.title }}</span></div>
      <article class="markdown-body">{{ page.content }}</article>
    </section>
  </div>
{% endblock %}
`;
}

function yamlString(value) {
  return JSON.stringify(String(value));
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
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
          reject(new Error("Unable to allocate a local port."));
        }
      });
    });
  });
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

function activate(context) {
  const browser = new WorkspaceDocBrowser(context);
  browser.activate();
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
