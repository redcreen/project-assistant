"use strict";

const cp = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const vscode = require("vscode");

const TASK_LABELS = {
  "bootstrap": "Bootstrap Project",
  "retrofit": "Retrofit Project",
  "docs-retrofit": "Retrofit Docs",
  "resume-readiness": "Check Resume Readiness",
  "continue": "Continue Snapshot",
  "progress": "Progress Snapshot",
  "handoff": "Handoff Snapshot",
  "validate-fast": "Fast Validation",
  "validate-deep": "Deep Validation",
  "capability-snapshot": "Capability Snapshot",
};

const STATUS_LABELS = {
  "queued": "Queued",
  "running": "Running",
  "completed": "Completed",
  "failed": "Failed",
  "cancelled": "Cancelled",
};

const EVENT_LABELS = {
  "task_queued": "Task queued",
  "task_running": "Task started",
  "task_completed": "Task completed",
  "task_failed": "Task failed",
  "resume_ready": "Ready to continue",
  "session_started": "Foreground session started",
  "session_stopped": "Foreground session stopped",
  "daemon_stopping": "Daemon stopping",
};

const SESSION_SCAN_LIMIT = 120;
const STOP_AFTER_CURRENT_TEXT = "做完手上工作停止";
const OPENAI_CODEX_EXTENSION_ID = "openai.chatgpt";
const OPENAI_CODEX_SCHEME = "openai-codex";
const OPENAI_CODEX_AUTHORITY = "route";
const OPENAI_CODEX_EDITOR_VIEW = "chatgpt.conversationEditor";
const CODEX_AUTO_RESUME_ATTACH_DELAY_MS = 900;
const AUTO_CODING_OFF = "off";
const AUTO_CODING_ON = "on";
const AUTO_CODING_STOP_AFTER_CURRENT = "stop-after-current";
const DAEMON_CONNECTED_CONTEXT = "projectAssistant.daemonConnected";
const AUTO_CODING_ACTIVE_CONTEXT = "projectAssistant.autoCodingActive";

class QueueItem extends vscode.TreeItem {
  constructor(label, collapsibleState = vscode.TreeItemCollapsibleState.None, options = {}) {
    super(label, collapsibleState);
    this.description = options.description;
    this.tooltip = options.tooltip;
    this.contextValue = options.contextValue;
    this.command = options.command;
    this.children = options.children || [];
    this.iconPath = options.iconPath;
  }
}

function dedupePaths(entries) {
  const seen = new Set();
  return entries.filter((entry) => {
    const key = `${entry.source}:${entry.path}`;
    if (!entry.path || seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function commandSpec(command, title, args = []) {
  return { command, title, arguments: args };
}

function shellQuote(value) {
  return `"${String(value).replace(/(["\\$`])/g, "\\$1")}"`;
}

function appleScriptQuote(value) {
  return String(value || "")
    .replaceAll("\\", "\\\\")
    .replaceAll("\"", "\\\"");
}

function existsAndExecutable(filePath) {
  try {
    fs.accessSync(filePath, fs.constants.X_OK);
    return true;
  } catch {
    return false;
  }
}

function findExecutableOnPath(name) {
  const pathValue = process.env.PATH || "";
  const dirs = pathValue.split(path.delimiter).filter(Boolean);
  const extensions = process.platform === "win32"
    ? (process.env.PATHEXT || ".EXE").split(";")
    : [""];

  for (const dir of dirs) {
    for (const ext of extensions) {
      const candidate = path.join(dir, process.platform === "win32" ? `${name}${ext}` : name);
      if (existsAndExecutable(candidate)) {
        return candidate;
      }
    }
  }
  return null;
}

function friendlyTaskLabel(taskType) {
  return TASK_LABELS[taskType] || taskType;
}

function friendlyStatus(status) {
  return STATUS_LABELS[status] || status || "Unknown";
}

function countSummary(counts = {}) {
  return `${counts.queued || 0} waiting · ${counts.running || 0} running · ${counts.completed || 0} done`;
}

function shortTime(value) {
  if (!value) {
    return "n/a";
  }
  try {
    return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return String(value);
  }
}

function buildEventLine(event) {
  const base = EVENT_LABELS[event.type] || event.type;
  if (event.taskType) {
    return `${base}: ${friendlyTaskLabel(event.taskType)}`;
  }
  return base;
}

function statusIcon(status) {
  if (status === "completed") {
    return new vscode.ThemeIcon("pass");
  }
  if (status === "failed") {
    return new vscode.ThemeIcon("error");
  }
  if (status === "running") {
    return new vscode.ThemeIcon("sync");
  }
  return new vscode.ThemeIcon("clock");
}

function markdownEscape(value) {
  return String(value || "")
    .replaceAll("\\", "\\\\")
    .replaceAll("`", "\\`");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function shortId(value) {
  return value ? String(value).slice(0, 8) : "n/a";
}

function safeJsonStringify(value) {
  try {
    return JSON.stringify(value);
  } catch {
    return "";
  }
}

function readTextIfExists(filePath) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return "";
  }
}

function extractMarkdownSection(text, heading) {
  const pattern = new RegExp(`^## ${heading.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\$&")}\\n([\\s\\S]*?)(?=^## |\\Z)`, "m");
  const match = text.match(pattern);
  return match ? match[1].trim() : "";
}

function markdownBulletItems(text) {
  const items = [];
  for (const rawLine of String(text || "").split(/\r?\n/)) {
    const stripped = rawLine.trim();
    if (stripped.startsWith("- ")) {
      items.push(stripped.slice(2).trim().replace(/^`|`$/g, ""));
      continue;
    }
    const numbered = stripped.match(/^\d+\.\s+(.*)$/);
    if (numbered) {
      items.push(numbered[1].trim().replace(/^`|`$/g, ""));
    }
  }
  return items.filter(Boolean);
}

function markdownCheckboxItems(text) {
  const items = [];
  for (const rawLine of String(text || "").split(/\r?\n/)) {
    const stripped = rawLine.trim();
    if (stripped.startsWith("- [ ] ")) {
      items.push({ status: "open", text: stripped.slice(6).trim().replace(/^`|`$/g, "") });
      continue;
    }
    if (stripped.startsWith("- [x] ") || stripped.startsWith("- [X] ")) {
      items.push({ status: "done", text: stripped.slice(6).trim().replace(/^`|`$/g, "") });
    }
  }
  return items.filter((item) => item.text);
}

function labeledMarkdownBullet(text, label) {
  const prefix = `- ${label}:`;
  for (const rawLine of String(text || "").split(/\r?\n/)) {
    const stripped = rawLine.trim();
    if (stripped.startsWith(prefix)) {
      return stripped.slice(prefix.length).trim().replace(/^`|`$/g, "");
    }
  }
  return "";
}

class ProjectAssistantProvider {
  constructor(extensionPath, output, statusBar, workspaceState) {
    this.extensionPath = extensionPath;
    this.output = output;
    this.statusBar = statusBar;
    this.workspaceState = workspaceState;
    this._onDidChangeTreeData = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    this.workspaceRoot = null;
    this.status = null;
    this.queue = [];
    this.lastEventId = 0;
    this.recentEvents = [];
    this.recentFiles = [];
    this.intervalHandle = null;
    this.watchers = [];
    this.cliResolution = null;
    this.lastError = null;
    this.workspaceSession = null;
    this.autoResumeInFlight = false;
    this.lastAutoResumeTriggerId = 0;
    this.lastAutoResumeAttemptAt = "";
    this.lastAutoResumeOutcome = null;
    this.autoCodingMode = AUTO_CODING_OFF;
  }

  activate(context) {
    this.workspaceRoot = this.getWorkspaceRoot();
    this.setupWatchers(context);
    this.startPolling(context);
  }

  async updateViewContexts() {
    await Promise.all([
      vscode.commands.executeCommand("setContext", DAEMON_CONNECTED_CONTEXT, Boolean(this.workspaceRoot && this.status)),
      vscode.commands.executeCommand(
        "setContext",
        AUTO_CODING_ACTIVE_CONTEXT,
        Boolean(this.workspaceRoot && (this.isAutoCodingEnabled() || this.isAutoCodingStoppingAfterCurrent())),
      ),
    ]);
  }

  getWorkspaceRoot() {
    const folder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
    return folder ? folder.uri.fsPath : null;
  }

  actionItem(label, description, command, icon, tooltip) {
    return new QueueItem(label, vscode.TreeItemCollapsibleState.None, {
      description,
      tooltip,
      iconPath: new vscode.ThemeIcon(icon),
      command: commandSpec(command, label),
      contextValue: "projectAssistantAction",
    });
  }

  infoItem(label, description, icon = "info", tooltip) {
    return new QueueItem(label, vscode.TreeItemCollapsibleState.None, {
      description,
      tooltip,
      iconPath: new vscode.ThemeIcon(icon),
    });
  }

  suggestionItem(label, description, command, icon, tooltip) {
    return this.actionItem(label, description, command, icon, tooltip);
  }

  hasOpenAICodexExtension() {
    return Boolean(vscode.extensions.getExtension(OPENAI_CODEX_EXTENSION_ID));
  }

  async ensureOpenAICodexExtension() {
    const extension = vscode.extensions.getExtension(OPENAI_CODEX_EXTENSION_ID);
    if (!extension) {
      return null;
    }
    if (!extension.isActive) {
      await extension.activate();
    }
    return extension;
  }

  getResumeTargetLabel() {
    const hasCodexExtension = this.hasOpenAICodexExtension();
    if (hasCodexExtension && this.workspaceSession) {
      return {
        description: "Exact VS Code Codex session",
        icon: "verified",
        tooltip: `Resume will open the exact saved Codex session ${this.workspaceSession.id} inside VS Code, then attach the latest resume pack files.`,
      };
    }
    if (hasCodexExtension) {
      return {
        description: "New VS Code Codex thread",
        icon: "sparkle",
        tooltip: "No exact saved session was found. Resume will open a new Codex thread in VS Code and attach the current resume pack files.",
      };
    }
    if (this.workspaceSession) {
      return {
        description: "CLI exact session fallback",
        icon: "terminal",
        tooltip: `The VS Code Codex extension is not available. Resume will fall back to Codex CLI and target saved session ${this.workspaceSession.id}.`,
      };
    }
    return {
      description: "CLI workspace fallback",
      icon: "terminal",
      tooltip: "The VS Code Codex extension is not available. Resume will fall back to the Codex CLI in this workspace.",
    };
  }

  resolveCliPath() {
    const config = vscode.workspace.getConfiguration();
    const configured = String(config.get("projectAssistant.cliPath", "") || "").trim();
    const candidates = [];

    if (configured) {
      const resolved = path.resolve(configured);
      if (!existsAndExecutable(resolved)) {
        throw new Error(
          `Configured CLI path does not exist: ${resolved}. Update projectAssistant.cliPath to a valid project-assistant wrapper.`,
        );
      }
      this.cliResolution = { path: resolved, source: "projectAssistant.cliPath" };
      return this.cliResolution;
    }

    if (this.workspaceRoot) {
      candidates.push(
        { path: path.join(this.workspaceRoot, "bin", "project-assistant"), source: "workspaceRoot/bin" },
      );
    }

    candidates.push(
      { path: path.join(this.extensionPath, "bin", "project-assistant"), source: "extension/bin" },
      { path: path.resolve(this.extensionPath, "..", "bin", "project-assistant"), source: "extension parent/bin" },
      { path: path.resolve(this.extensionPath, "..", "..", "bin", "project-assistant"), source: "extension grandparent/bin" },
      { path: path.join(os.homedir(), ".codex", "skills", "project-assistant", "bin", "project-assistant"), source: "~/.codex/skills/project-assistant" },
    );

    for (const candidate of dedupePaths(candidates)) {
      if (existsAndExecutable(candidate.path)) {
        this.cliResolution = candidate;
        return candidate;
      }
    }

    const onPath = findExecutableOnPath("project-assistant");
    if (onPath) {
      this.cliResolution = { path: onPath, source: "PATH" };
      return this.cliResolution;
    }

    throw new Error("Cannot find the project-assistant CLI. Open settings and set projectAssistant.cliPath.");
  }

  resolveCodexPath() {
    const configured = String(vscode.workspace.getConfiguration().get("projectAssistant.codexPath", "") || "").trim();
    if (configured) {
      const resolved = path.resolve(configured);
      if (!existsAndExecutable(resolved)) {
        throw new Error(`Configured Codex path does not exist: ${resolved}. Update projectAssistant.codexPath.`);
      }
      return resolved;
    }
    const onPath = findExecutableOnPath("codex");
    if (onPath) {
      return onPath;
    }
    throw new Error("Cannot find the Codex CLI. Install codex or set projectAssistant.codexPath.");
  }

  normalizePath(value) {
    if (!value) {
      return null;
    }
    try {
      return fs.realpathSync.native(path.resolve(value));
    } catch {
      return path.resolve(value);
    }
  }

  getWorkspaceDisplayName() {
    if (!this.workspaceRoot) {
      return "unknown-workspace";
    }
    return path.basename(this.workspaceRoot) || this.workspaceRoot;
  }

  readExecutionContinuityFallback() {
    if (!this.workspaceRoot) {
      return {
        currentCheckpoint: "n/a",
        nextAction: "n/a",
        nextActionSource: "none",
        remainingExecutionTasks: [],
      };
    }
    const statusText = readTextIfExists(path.join(this.workspaceRoot, ".codex", "status.md"));
    const planText = readTextIfExists(path.join(this.workspaceRoot, ".codex", "plan.md"));
    const statusExecution = extractMarkdownSection(statusText, "Current Execution Line");
    const planExecution = extractMarkdownSection(planText, "Current Execution Line");
    const statusNextActions = extractMarkdownSection(statusText, "Next 3 Actions");
    const planTasks = extractMarkdownSection(planText, "Execution Tasks");
    const checkpoint = (
      labeledMarkdownBullet(statusExecution, "Runway")
      || labeledMarkdownBullet(planExecution, "Runway")
      || labeledMarkdownBullet(statusExecution, "Objective")
      || labeledMarkdownBullet(planExecution, "Objective")
      || "n/a"
    );
    const nextThree = markdownBulletItems(statusNextActions);
    const openTasks = markdownCheckboxItems(planTasks)
      .filter((item) => item.status === "open")
      .map((item) => item.text);
    return {
      currentCheckpoint: checkpoint,
      nextAction: openTasks[0] || nextThree[0] || "n/a",
      nextActionSource: openTasks.length ? "plan.execution-tasks" : (nextThree.length ? "status.next-3" : "none"),
      remainingExecutionTasks: openTasks.slice(0, 3),
    };
  }

  getExecutionContinuity() {
    const fallback = this.readExecutionContinuityFallback();
    const remaining = Array.isArray(this.status && this.status.remainingExecutionTasks)
      ? this.status.remainingExecutionTasks.filter(Boolean).map((item) => String(item))
      : fallback.remainingExecutionTasks;
    return {
      currentCheckpoint: String((this.status && this.status.currentCheckpoint) || fallback.currentCheckpoint || "n/a"),
      nextAction: String((this.status && this.status.nextAction) || fallback.nextAction || "n/a"),
      nextActionSource: String((this.status && this.status.nextActionSource) || fallback.nextActionSource || "none"),
      remainingExecutionTasks: remaining,
    };
  }

  getNextActionBasis() {
    const continuity = this.getExecutionContinuity();
    const source = continuity.nextActionSource || "none";
    if (source === "plan.execution-tasks") {
      return {
        summary: "First open execution task in .codex/plan.md",
        detail: "The next step comes from the first unchecked item under the Execution Tasks section in .codex/plan.md.",
        primaryDoc: ".codex/plan.md",
        secondaryDoc: ".codex/status.md",
      };
    }
    if (source === "status.next-3") {
      return {
        summary: "First item in .codex/status.md Next 3 Actions",
        detail: "The next step comes from the first bullet under the Next 3 Actions section in .codex/status.md.",
        primaryDoc: ".codex/status.md",
        secondaryDoc: ".codex/plan.md",
      };
    }
    return {
      summary: "No durable next-step source found yet",
      detail: "Project Assistant could not derive a clear next action from .codex/plan.md or .codex/status.md yet.",
      primaryDoc: ".codex/status.md",
      secondaryDoc: ".codex/plan.md",
    };
  }

  isMacOS() {
    return process.platform === "darwin";
  }

  isExactSessionAutoSubmitEnabled() {
    return Boolean(vscode.workspace.getConfiguration().get("projectAssistant.experimentalExactSessionAutoSubmit", false));
  }

  isAutoResumeOnReadyEnabled() {
    return Boolean(vscode.workspace.getConfiguration().get("projectAssistant.autoResumeOnReady", false));
  }

  getAutoResumeStrategy() {
    const value = String(vscode.workspace.getConfiguration().get("projectAssistant.autoResumeStrategy", "new-thread") || "new-thread").trim();
    return value === "new-thread" ? "new-thread" : "exact-session";
  }

  getAutoResumeDelayMs() {
    const value = Number(vscode.workspace.getConfiguration().get("projectAssistant.autoResumeDelayMs", 1200));
    if (!Number.isFinite(value) || value < 0) {
      return 1200;
    }
    return value;
  }

  shouldAutoResumeFallbackToNewThread() {
    return Boolean(vscode.workspace.getConfiguration().get("projectAssistant.autoResumeFallbackToNewThread", true));
  }

  isAutomaticExactSessionResumeEnabled() {
    return Boolean(vscode.workspace.getConfiguration().get("projectAssistant.experimentalAutoResumeIntoExactSession", false));
  }

  getAutoResumeCooldownMs() {
    const value = Number(vscode.workspace.getConfiguration().get("projectAssistant.autoResumeCooldownMs", 15000));
    if (!Number.isFinite(value) || value < 0) {
      return 15000;
    }
    return value;
  }

  canAutoSubmitIntoExactSession() {
    return Boolean(
      this.workspaceRoot
      && this.workspaceSession
      && this.hasOpenAICodexExtension()
      && this.isMacOS()
      && this.isExactSessionAutoSubmitEnabled(),
    );
  }

  canAutoResumeIntoExactSession() {
    return Boolean(this.canAutoSubmitIntoExactSession() && this.isAutomaticExactSessionResumeEnabled());
  }

  getResumeAutomationSummary() {
    if (this.canAutoSubmitIntoExactSession()) {
      return {
        description: "Exact session auto-send enabled",
        icon: "send",
        tooltip: "When an exact saved Codex session is found, Project Assistant will try to paste and send the generated resume prompt into that session on macOS.",
      };
    }
    if (this.isExactSessionAutoSubmitEnabled() && !this.isMacOS()) {
      return {
        description: "Exact session auto-send unavailable on this OS",
        icon: "warning",
        tooltip: "Experimental exact-session auto-send is currently implemented only for local macOS VS Code hosts. This workspace will fall back to opening the session and copying the prompt.",
      };
    }
    return {
      description: "Manual send fallback",
      icon: "clippy",
      tooltip: "Project Assistant will open the matching Codex session, attach the resume pack, and copy the generated prompt to the clipboard.",
    };
  }

  getAutoResumeMonitorSummary() {
    if (!this.isAutoCodingEnabled() && !this.isAutoCodingStoppingAfterCurrent()) {
      return {
        description: "Off",
        icon: "circle-slash",
        tooltip: "Auto Coding is off, so daemon completion and resume-ready events stay visible but will not automatically launch another Codex turn.",
      };
    }
    if (this.isAutoCodingStoppingAfterCurrent()) {
      return {
        description: "Stopping after current turn",
        icon: "debug-stop",
        tooltip: "Auto Coding has been asked to stop. The current turn is allowed to settle, but no new automatic turn will start after that.",
      };
    }
    if (this.getAutoResumeStrategy() === "new-thread") {
      return {
        description: "On · new thread strategy",
        icon: "sync",
        tooltip: "When daemon events indicate that this workspace is ready to continue, Project Assistant will start a fresh Codex thread and auto-submit the generated resume request.",
      };
    }
    if (this.canAutoResumeIntoExactSession()) {
      return {
        description: "On · exact session strategy",
        icon: "sync",
        tooltip: "When daemon events indicate that this workspace is ready to continue, Project Assistant will open the exact saved Codex session and try to auto-send the generated resume prompt there.",
      };
    }
    if (this.getAutoResumeStrategy() === "exact-session" && this.canAutoSubmitIntoExactSession()) {
      return {
        description: "On · exact session blocked by safety guard",
        icon: "warning",
        tooltip: "Manual exact-session resume is still available, but daemon-driven auto-resume will not paste into an existing session unless the extra experimental exact-session auto-resume setting is enabled.",
      };
    }
    if (this.shouldAutoResumeFallbackToNewThread()) {
      return {
        description: "On · exact session with new-thread fallback",
        icon: "sync",
        tooltip: "Auto-resume prefers exact-session in config, but the safety guard keeps daemon-driven resume on a fresh Codex thread unless explicit exact-session auto-resume is enabled.",
      };
    }
    return {
      description: "On · waiting for exact-session auto-send support",
      icon: "warning",
      tooltip: "Auto-resume monitoring is enabled, but exact-session auto-resume is not currently allowed in this environment. The host will log the trigger and wait unless a safer path is configured.",
    };
  }

  getCodexHome() {
    return path.join(os.homedir(), ".codex");
  }

  getWorkspaceStateKey(suffix) {
    const root = this.workspaceRoot || "no-workspace";
    return `projectAssistant.${suffix}.${Buffer.from(root).toString("base64")}`;
  }

  restoreAutoCodingState() {
    if (!this.workspaceState || !this.workspaceRoot) {
      this.autoCodingMode = AUTO_CODING_OFF;
      return;
    }
    const saved = String(this.workspaceState.get(this.getWorkspaceStateKey("autoCodingMode"), "") || "").trim();
    if ([AUTO_CODING_OFF, AUTO_CODING_ON, AUTO_CODING_STOP_AFTER_CURRENT].includes(saved)) {
      this.autoCodingMode = saved;
      return;
    }
    this.autoCodingMode = AUTO_CODING_OFF;
  }

  persistAutoCodingState() {
    if (!this.workspaceState || !this.workspaceRoot) {
      return;
    }
    void this.workspaceState.update(this.getWorkspaceStateKey("autoCodingMode"), this.autoCodingMode || AUTO_CODING_OFF);
  }

  isAutoCodingEnabled() {
    return this.autoCodingMode === AUTO_CODING_ON;
  }

  isAutoCodingStoppingAfterCurrent() {
    return this.autoCodingMode === AUTO_CODING_STOP_AFTER_CURRENT;
  }

  hasActionablePlan(continuity = this.getExecutionContinuity()) {
    return Boolean(
      continuity
      && continuity.nextAction
      && continuity.nextAction !== "n/a"
      && continuity.nextActionSource
      && continuity.nextActionSource !== "none",
    );
  }

  getAutoCodingSummary() {
    const continuity = this.getExecutionContinuity();
    if (this.isAutoCodingStoppingAfterCurrent()) {
      return {
        description: "Stopping after current turn",
        icon: "debug-stop",
        tooltip: `Auto Coding will not launch another automatic turn after the current work settles. Current planned step: ${continuity.nextAction}.`,
      };
    }
    if (this.isAutoCodingEnabled()) {
      if (!this.hasActionablePlan(continuity)) {
        return {
          description: "On, but waiting for a plan",
          icon: "warning",
          tooltip: "Auto Coding is enabled, but Project Assistant cannot find a durable next action in .codex/plan.md or .codex/status.md yet.",
        };
      }
      return {
        description: `On -> ${continuity.nextAction}`,
        icon: "rocket",
        tooltip: `Auto Coding will keep resuming from the durable plan. Next action source: ${continuity.nextActionSource}.`,
      };
    }
    return {
      description: "Off",
      icon: "circle-slash",
      tooltip: "Auto Coding is off. Project Assistant will not automatically launch the next coding turn.",
    };
  }

  restoreAutoResumeState() {
    if (!this.workspaceState || !this.workspaceRoot) {
      return;
    }
    this.lastAutoResumeTriggerId = Number(this.workspaceState.get(this.getWorkspaceStateKey("lastAutoResumeTriggerId"), 0)) || 0;
    this.lastAutoResumeAttemptAt = String(this.workspaceState.get(this.getWorkspaceStateKey("lastAutoResumeAttemptAt"), "") || "");
    const rawOutcome = String(this.workspaceState.get(this.getWorkspaceStateKey("lastAutoResumeOutcome"), "") || "");
    if (!rawOutcome) {
      this.lastAutoResumeOutcome = null;
      return;
    }
    try {
      this.lastAutoResumeOutcome = JSON.parse(rawOutcome);
    } catch {
      this.lastAutoResumeOutcome = null;
    }
  }

  persistAutoResumeState() {
    if (!this.workspaceState || !this.workspaceRoot) {
      return;
    }
    void this.workspaceState.update(this.getWorkspaceStateKey("lastAutoResumeTriggerId"), this.lastAutoResumeTriggerId);
    void this.workspaceState.update(this.getWorkspaceStateKey("lastAutoResumeAttemptAt"), this.lastAutoResumeAttemptAt || "");
    void this.workspaceState.update(this.getWorkspaceStateKey("lastAutoResumeOutcome"), safeJsonStringify(this.lastAutoResumeOutcome || null));
  }

  recordAutoResumeOutcome(outcome) {
    this.lastAutoResumeAttemptAt = new Date().toISOString();
    this.lastAutoResumeOutcome = {
      at: this.lastAutoResumeAttemptAt,
      ...outcome,
    };
    this.persistAutoResumeState();
  }

  describeLastAutoResumeOutcome() {
    if (!this.lastAutoResumeOutcome) {
      return {
        description: "No automatic resume yet",
        icon: "clock",
        tooltip: "No daemon-triggered automatic resume attempt has run for this workspace yet.",
      };
    }
    const outcome = this.lastAutoResumeOutcome;
    if (outcome.status === "succeeded") {
      return {
        description: `${outcome.label || "Succeeded"} · ${shortTime(outcome.at)}`,
        icon: "pass",
        tooltip: `Automatic resume succeeded at ${outcome.at}. Trigger: ${outcome.triggerType || "n/a"} (#${outcome.triggerId || "n/a"}). Mode: ${outcome.mode || "n/a"}.`,
      };
    }
    if (outcome.status === "skipped") {
      return {
        description: `${outcome.label || "Skipped"} · ${shortTime(outcome.at)}`,
        icon: "warning",
        tooltip: `Automatic resume was skipped at ${outcome.at}. Reason: ${outcome.reason || "n/a"}. Trigger: ${outcome.triggerType || "n/a"} (#${outcome.triggerId || "n/a"}).`,
      };
    }
    return {
      description: `${outcome.label || "Failed"} · ${shortTime(outcome.at)}`,
      icon: "error",
      tooltip: `Automatic resume failed at ${outcome.at}. Reason: ${outcome.reason || "n/a"}. Trigger: ${outcome.triggerType || "n/a"} (#${outcome.triggerId || "n/a"}).`,
    };
  }

  readSessionTitleMap() {
    const indexPath = path.join(this.getCodexHome(), "session_index.jsonl");
    const titles = new Map();
    let content = "";
    try {
      content = fs.readFileSync(indexPath, "utf8");
    } catch {
      return titles;
    }
    for (const line of content.split(/\r?\n/)) {
      if (!line.trim()) {
        continue;
      }
      try {
        const row = JSON.parse(line);
        if (row.id && row.thread_name) {
          titles.set(String(row.id), String(row.thread_name));
        }
      } catch {
        continue;
      }
    }
    return titles;
  }

  listRecentSessionFiles() {
    const root = path.join(this.getCodexHome(), "sessions");
    const collected = [];

    const visit = (dir) => {
      let entries = [];
      try {
        entries = fs.readdirSync(dir, { withFileTypes: true });
      } catch {
        return;
      }
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          visit(fullPath);
          continue;
        }
        if (!entry.isFile() || !entry.name.endsWith(".jsonl")) {
          continue;
        }
        try {
          const stat = fs.statSync(fullPath);
          collected.push({ path: fullPath, mtimeMs: stat.mtimeMs });
        } catch {
          continue;
        }
      }
    };

    visit(root);
    return collected
      .sort((a, b) => b.mtimeMs - a.mtimeMs)
      .slice(0, SESSION_SCAN_LIMIT);
  }

  readSessionMeta(filePath) {
    let content = "";
    try {
      content = fs.readFileSync(filePath, "utf8");
    } catch {
      return null;
    }
    for (const line of content.split(/\r?\n/)) {
      if (!line.trim()) {
        continue;
      }
      try {
        const payload = JSON.parse(line);
        if (payload.type === "session_meta" && payload.payload) {
          return payload.payload;
        }
      } catch {
        continue;
      }
    }
    return null;
  }

  findLatestWorkspaceSession() {
    const normalizedWorkspace = this.normalizePath(this.workspaceRoot);
    if (!normalizedWorkspace) {
      return null;
    }
    const titles = this.readSessionTitleMap();
    for (const entry of this.listRecentSessionFiles()) {
      const meta = this.readSessionMeta(entry.path);
      if (!meta || !meta.cwd || !meta.id) {
        continue;
      }
      if (this.normalizePath(meta.cwd) !== normalizedWorkspace) {
        continue;
      }
      return {
        id: String(meta.id),
        threadName: String(meta.thread_name || meta.title || titles.get(String(meta.id)) || meta.id),
        updatedAt: String(meta.timestamp || ""),
        cwd: String(meta.cwd),
        sourceFile: entry.path,
      };
    }
    return null;
  }

  async runCli(args, expectJson = true) {
    const cli = this.resolveCliPath();
    return new Promise((resolve, reject) => {
      cp.execFile(cli.path, args, { cwd: this.workspaceRoot || this.extensionPath }, (error, stdout, stderr) => {
        if (error) {
          reject(new Error((stderr || stdout || error.message).trim()));
          return;
        }
        if (!expectJson) {
          resolve(stdout);
          return;
        }
        try {
          resolve(JSON.parse(stdout));
        } catch {
          reject(new Error(`Failed to parse JSON from ${cli.path}: ${stdout}`));
        }
      });
    });
  }

  async runCommand(label, work) {
    try {
      return await work();
    } catch (error) {
      const message = String(error && error.message ? error.message : error);
      this.lastError = message;
      this.output.appendLine(`${label}: ${message}`);
      vscode.window.showErrorMessage(`Project Assistant: ${message}`);
      this._onDidChangeTreeData.fire();
      return null;
    }
  }

  async refresh() {
    this.workspaceRoot = this.getWorkspaceRoot();
    if (!this.workspaceRoot) {
      this.status = null;
      this.queue = [];
      this.cliResolution = null;
      this.lastError = null;
      this.setStatusBar("PA: open a workspace", "Open a local workspace to use Project Assistant.", undefined);
      await this.updateViewContexts();
      this._onDidChangeTreeData.fire();
      return;
    }
    try {
      this.restoreAutoCodingState();
      this.restoreAutoResumeState();
      this.resolveCliPath();
      this.status = await this.runCli(["daemon", "status", this.workspaceRoot, "--json"]);
      this.workspaceSession = this.findLatestWorkspaceSession();
      const queuePayload = await this.runCli(["queue", this.workspaceRoot, "--json"]);
      this.queue = queuePayload.tasks || [];
      const events = await this.runCli(
        ["daemon", "events", this.workspaceRoot, "--since-id", String(this.lastEventId), "--limit", "100", "--json"],
      );
      for (const item of events) {
        this.lastEventId = Math.max(this.lastEventId, Number(item.id || 0));
        this.recentEvents.push(item);
        this.output.appendLine(`[${item.timestamp}] ${buildEventLine(item)}`);
      }
      this.recentEvents = this.recentEvents.slice(-15);
      this.lastError = null;
      if (this.isAutoCodingStoppingAfterCurrent() && !this.autoResumeInFlight) {
        this.autoCodingMode = AUTO_CODING_OFF;
        this.persistAutoCodingState();
      }
      const counts = this.status.queueSummary || {};
      const continuity = this.getExecutionContinuity();
      const text = this.status.resumeReady
        ? `PA: Ready to continue · ${counts.running || 0} running`
        : `PA: ${friendlyStatus(this.status.status)} · ${counts.running || 0} running`;
      const tooltip = [
        `Stage: ${this.status.currentPhase || "n/a"}`,
        `Slice: ${this.status.activeSlice || "n/a"}`,
        `Checkpoint: ${continuity.currentCheckpoint || "n/a"}`,
        `Next: ${continuity.nextAction || "n/a"}`,
        `Queue: ${countSummary(counts)}`,
      ].join("\n");
      const command = this.status.resumeReady ? "projectAssistant.resumeCodex" : "projectAssistant.refresh";
      this.setStatusBar(text, tooltip, command);
      await this.maybeAutoResumeFromDaemonEvents(events);
    } catch (error) {
      this.status = null;
      this.queue = [];
      this.lastError = String(error && error.message ? error.message : error);
      this.workspaceSession = null;
      if (this.lastError.includes("Cannot find the project-assistant CLI")) {
        this.setStatusBar("PA: set CLI path", this.lastError, "projectAssistant.configureCliPath");
      } else {
        this.setStatusBar("PA: daemon offline", this.lastError, "projectAssistant.startDaemon");
      }
    }
    await this.updateViewContexts();
    this._onDidChangeTreeData.fire();
  }

  setStatusBar(text, tooltip, command = "projectAssistant.refresh") {
    this.statusBar.text = text;
    this.statusBar.tooltip = tooltip;
    this.statusBar.command = command;
    this.statusBar.show();
  }

  startPolling(context) {
    const intervalMs = Number(vscode.workspace.getConfiguration().get("projectAssistant.pollIntervalMs", 2000));
    if (this.intervalHandle) {
      clearInterval(this.intervalHandle);
    }
    this.intervalHandle = setInterval(() => {
      this.refresh().catch((error) => {
        this.output.appendLine(String(error));
      });
    }, intervalMs);
    context.subscriptions.push({ dispose: () => clearInterval(this.intervalHandle) });
    this.refresh().catch((error) => this.output.appendLine(String(error)));
  }

  setupWatchers(context) {
    const folder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
    if (!folder) {
      return;
    }
    const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(folder, "**/*"));
    watcher.onDidCreate((uri) => this.trackRecentFile("created", uri), null, context.subscriptions);
    watcher.onDidChange((uri) => this.trackRecentFile("changed", uri), null, context.subscriptions);
    watcher.onDidDelete((uri) => this.trackRecentFile("deleted", uri), null, context.subscriptions);
    context.subscriptions.push(watcher);
    this.watchers.push(watcher);
  }

  trackRecentFile(kind, uri) {
    const workspaceRoot = this.workspaceRoot;
    if (!workspaceRoot) {
      return;
    }
    const relative = path.relative(workspaceRoot, uri.fsPath);
    if (!relative || relative.startsWith(".git") || relative.includes("node_modules") || relative.includes(".codex/daemon")) {
      return;
    }
    this.recentFiles.unshift({ kind, relative, at: new Date().toISOString() });
    this.recentFiles = this.recentFiles.slice(0, 10);
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element) {
    return element;
  }

  renderDisconnectedState() {
    const actions = [
      this.actionItem(
        "Reload window",
        "Refresh VS Code itself",
        "projectAssistant.reloadWindow",
        "debug-restart",
        "Reload the current VS Code window so the updated host extension is reactivated.",
      ),
      this.actionItem(
        "Start background service",
        "Connect this workspace",
        "projectAssistant.startDaemon",
        "play-circle",
        "Start the per-workspace daemon so queue and status can refresh.",
      ),
      this.actionItem(
        "Set CLI path",
        "Fix project-assistant discovery",
        "projectAssistant.configureCliPath",
        "gear",
        "Open settings and set projectAssistant.cliPath to the project-assistant wrapper.",
      ),
      this.actionItem(
        "Open host log",
        "See the raw extension output",
        "projectAssistant.showOutput",
        "output",
        "Show the Project Assistant output channel.",
      ),
    ];

    const summary = [
      this.infoItem("Workspace", this.workspaceRoot ? path.basename(this.workspaceRoot) : "No workspace", "folder"),
      this.infoItem(
        "CLI",
        this.cliResolution ? `${this.cliResolution.path} (${this.cliResolution.source})` : "Not resolved yet",
        this.cliResolution ? "terminal" : "warning",
      ),
    ];

    if (this.lastError) {
      summary.push(this.infoItem("What is blocking it", this.lastError, "error"));
    }

    return [
      new QueueItem("Start Here", vscode.TreeItemCollapsibleState.Expanded, { children: actions, iconPath: new vscode.ThemeIcon("rocket") }),
      new QueueItem("Connection Status", vscode.TreeItemCollapsibleState.Expanded, { children: summary, iconPath: new vscode.ThemeIcon("pulse") }),
    ];
  }

  renderConnectedState() {
    const counts = this.status.queueSummary || {};
    const activeTasks = this.queue.filter((task) => task.status === "queued" || task.status === "running");
    const resumeTarget = this.getResumeTargetLabel();
    const continuity = this.getExecutionContinuity();
    const basis = this.getNextActionBasis();

    const executionChildren = [
      this.infoItem(
        "Doing now",
        continuity.currentCheckpoint,
        "debug-step-over",
        "This is the active checkpoint Project Assistant treats as the current execution thread.",
      ),
      this.infoItem(
        "Next step",
        continuity.nextAction,
        "arrow-right",
        `Next action source: ${continuity.nextActionSource}`,
      ),
      this.infoItem(
        "Why this is next",
        basis.summary,
        "link",
        basis.detail,
      ),
      this.actionItem(
        "Open next-step source",
        basis.primaryDoc,
        "projectAssistant.openNextActionSource",
        "preview",
        `${basis.detail}\nPrimary source: ${basis.primaryDoc}`,
      ),
      this.actionItem(
        "Open live status",
        ".codex/status.md",
        "projectAssistant.openStatusDoc",
        "book",
        "Open the live execution truth for this workspace.",
      ),
      this.actionItem(
        "Open live plan",
        ".codex/plan.md",
        "projectAssistant.openPlanDoc",
        "checklist",
        "Open the current durable execution plan for this workspace.",
      ),
    ];

    const summaryChildren = [
      this.infoItem("Background service", friendlyStatus(this.status.status), "server-process"),
      this.infoItem("Auto coding", this.getAutoCodingSummary().description, this.getAutoCodingSummary().icon, this.getAutoCodingSummary().tooltip),
      this.infoItem("Ready to continue", this.status.resumeReady ? "Yes" : "Not yet", this.status.resumeReady ? "pass" : "clock"),
      this.infoItem("Current stage", String(this.status.currentPhase || "n/a"), "milestone"),
      this.infoItem("Current slice", String(this.status.activeSlice || "n/a"), "target"),
      this.infoItem("Queue", countSummary(counts), "list-ordered"),
      this.infoItem("Last auto-resume", this.describeLastAutoResumeOutcome().description, this.describeLastAutoResumeOutcome().icon, this.describeLastAutoResumeOutcome().tooltip),
    ];

    const detailChildren = [
      this.infoItem("Work policy", "Keep going by default until you tell the assistant to stop", "rocket", "Recommended operating mode: let Project Assistant keep moving until you explicitly say “做完手上工作停止”."),
      this.infoItem("Resume automation", this.getResumeAutomationSummary().description, this.getResumeAutomationSummary().icon, this.getResumeAutomationSummary().tooltip),
      this.infoItem("Auto-resume monitor", this.getAutoResumeMonitorSummary().description, this.getAutoResumeMonitorSummary().icon, this.getAutoResumeMonitorSummary().tooltip),
      this.infoItem("Current checkpoint", continuity.currentCheckpoint, "debug-step-over", `Current checkpoint continuity comes from ${this.status && this.status.currentCheckpoint ? "daemon status" : ".codex/status.md / .codex/plan.md"} and is what auto-resume treats as already-known truth.`),
      this.infoItem("Next action", continuity.nextAction, "arrow-right", `Next action source: ${continuity.nextActionSource}`),
      this.actionItem(
        "Recent Codex session",
        this.workspaceSession ? `${this.workspaceSession.threadName} · ${this.workspaceSession.id.slice(0, 8)}` : "No matching session found yet",
        "projectAssistant.openRecentCodexSession",
        this.workspaceSession ? "run" : "clock",
        this.workspaceSession ? `Session: ${this.workspaceSession.id}\nUpdated: ${shortTime(this.workspaceSession.updatedAt)}\nSource: ${this.workspaceSession.sourceFile}` : "No recent Codex session was found for this workspace.",
      ),
      this.infoItem(
        "Resume target",
        resumeTarget.description,
        resumeTarget.icon,
        resumeTarget.tooltip,
      ),
      this.infoItem(
        "CLI",
        this.cliResolution ? `${this.cliResolution.path} (${this.cliResolution.source})` : "Unknown",
        "terminal",
      ),
    ];

    const nowChildren = [];
    if (this.isAutoCodingEnabled() || this.isAutoCodingStoppingAfterCurrent()) {
      nowChildren.push(
        this.actionItem(
          "Stop auto coding",
          this.isAutoCodingStoppingAfterCurrent() ? "Already draining the current turn" : "Finish the current turn, then stop",
          "projectAssistant.stopAutoCoding",
          "primitive-square",
          "Turn Auto Coding off. The current coding turn is not interrupted, but Project Assistant will stop launching new automatic turns after it settles.",
        ),
      );
    } else {
      nowChildren.push(
        this.actionItem(
          "Start auto coding",
          this.hasActionablePlan(continuity) ? `Follow ${continuity.nextAction}` : "Needs a next action in .codex/plan.md",
          "projectAssistant.startAutoCoding",
          "rocket",
          this.hasActionablePlan(continuity)
            ? "Turn Auto Coding on. Project Assistant will keep resuming from the durable plan and immediately try to continue if the workspace is already ready."
            : "Turn Auto Coding on once .codex/plan.md or .codex/status.md contains a durable next action.",
        ),
      );
    }
    nowChildren.push(
      this.actionItem(
        "Resume last Codex session",
        this.status.resumeReady ? "Continue working now" : "Open the matched session before it is ready",
        "projectAssistant.resumeCodex",
        "run",
        "Open the matching Codex session in VS Code when possible, otherwise fall back to the workspace-safe CLI resume path.",
      ),
    );
    nowChildren.push(
      this.actionItem(
        "Open continue view",
        "See the current execution line in Markdown",
        "projectAssistant.manualContinue",
        "book",
        "Render project-assistant continue and open it as Markdown preview.",
      ),
    );
    nowChildren.push(
      this.actionItem(
        activeTasks.length ? "Open progress view" : "Queue progress snapshot",
        activeTasks.length ? "Watch the maintainer view while work is moving" : "Refresh the maintainer dashboard in the background",
        activeTasks.length ? "projectAssistant.openProgressInTerminal" : "projectAssistant.showProgress",
        "pulse",
        activeTasks.length ? "Render project-assistant progress and open it as Markdown preview." : "Queue a background progress snapshot task.",
      ),
    );
    nowChildren.push(
      this.actionItem(
        "Create a handoff point",
        "Prepare a clean resume pack before switching context",
        "projectAssistant.openHandoffInTerminal",
        "archive",
        "Render project-assistant handoff and open it as Markdown preview.",
      ),
    );

    const toolChildren = [
      this.actionItem(
        "Open next-step source",
        basis.primaryDoc,
        "projectAssistant.openNextActionSource",
        "preview",
        `${basis.detail}\nPrimary source: ${basis.primaryDoc}`,
      ),
      this.actionItem(
        "Open live status",
        ".codex/status.md",
        "projectAssistant.openStatusDoc",
        "book",
        "Open the live execution truth for this workspace.",
      ),
      this.actionItem(
        "Open live plan",
        ".codex/plan.md",
        "projectAssistant.openPlanDoc",
        "checklist",
        "Open the current durable execution plan for this workspace.",
      ),
      this.actionItem(
        "Open recent Codex session",
        this.workspaceSession ? `${this.workspaceSession.threadName} · ${shortId(this.workspaceSession.id)}` : "No matching session found yet",
        "projectAssistant.openRecentCodexSession",
        this.workspaceSession ? "preview" : "clock",
        this.workspaceSession ? `Session: ${this.workspaceSession.id}\nUpdated: ${shortTime(this.workspaceSession.updatedAt)}` : "No recent Codex session was found for this workspace.",
      ),
      this.actionItem(
        "Start new auto resume thread",
        "Experimental fallback for a fresh Codex thread",
        "projectAssistant.autoResumeCodex",
        "send",
        "Start a fresh Codex thread inside VS Code and auto-submit a generated Project Assistant resume request.",
      ),
      this.actionItem(
        "Queue continue snapshot",
        "Refresh the continue panel in the background",
        "projectAssistant.oneClickContinue",
        "history",
        "Queue a background continue snapshot task.",
      ),
      this.actionItem(
        "Queue handoff snapshot",
        "Prepare a background handoff snapshot",
        "projectAssistant.showHandoff",
        "archive",
        "Queue a background handoff snapshot task.",
      ),
      this.actionItem(
        "Open retrofit view",
        "Render project-assistant retrofit as Markdown",
        "projectAssistant.openRetrofitInTerminal",
        "tools",
        "Render project-assistant retrofit output and open it as Markdown preview.",
      ),
      this.actionItem(
        "Refresh status",
        "Poll daemon status now",
        "projectAssistant.refresh",
        "refresh",
        "Refresh daemon status, queue, and events now.",
      ),
      this.actionItem(
        "Reload window",
        "Refresh VS Code itself",
        "projectAssistant.reloadWindow",
        "debug-restart",
        "Reload the current VS Code window so updated commands and UI take effect immediately.",
      ),
      this.actionItem(
        "Stop background service",
        "Disconnect this workspace",
        "projectAssistant.stopDaemon",
        "debug-stop",
        "Stop the daemon for this workspace.",
      ),
      this.actionItem(
        "Copy stop instruction",
        "Copy the phrase that tells the assistant to stop after the current work",
        "projectAssistant.copyStopInstruction",
        "clippy",
        "Copies “做完手上工作停止” to the clipboard.",
      ),
      this.actionItem(
        "Open host log",
        "See the raw extension output",
        "projectAssistant.showOutput",
        "output",
        "Show the Project Assistant output channel.",
      ),
    ];

    const queueItems = this.queue.map((task) => {
      const duration = task.durationSeconds ? ` · ${task.durationSeconds}s` : "";
      const description = `${friendlyStatus(task.status)} · ${task.etaBand || "n/a"}${duration}`;
      const tooltip = [
        `Task: ${friendlyTaskLabel(task.taskType)}`,
        `Status: ${friendlyStatus(task.status)}`,
        `Created: ${shortTime(task.createdAt)}`,
        `Started: ${shortTime(task.startedAt)}`,
        `Finished: ${shortTime(task.finishedAt)}`,
        `Log: ${task.outputPath}`,
      ].join("\n");
      return new QueueItem(friendlyTaskLabel(task.taskType), vscode.TreeItemCollapsibleState.None, {
        description,
        tooltip,
        iconPath: statusIcon(task.status),
        contextValue: "projectAssistantTask",
        command: commandSpec("projectAssistant.openTaskLog", "Open Task Log", [task]),
      });
    });

    const activeQueueChildren = queueItems.filter((item, index) => {
      const task = this.queue[index];
      return task.status === "queued" || task.status === "running";
    });

    const finishedPairs = this.queue
      .map((task, index) => ({ task, item: queueItems[index] }))
      .filter(({ task }) => task.status !== "queued" && task.status !== "running")
      .sort((a, b) => String(b.task.finishedAt || b.task.createdAt || "").localeCompare(String(a.task.finishedAt || a.task.createdAt || "")));

    const recentFinishedChildren = finishedPairs.slice(0, 8).map((entry) => entry.item);
    const olderFinishedChildren = finishedPairs.slice(8).map((entry) => entry.item);

    const queueChildren = [
      new QueueItem("Now", vscode.TreeItemCollapsibleState.Expanded, {
        description: String(activeQueueChildren.length),
        children: activeQueueChildren.length ? activeQueueChildren : [this.infoItem("No active tasks", "Nothing is queued or running right now.", "clock")],
        iconPath: new vscode.ThemeIcon("play"),
      }),
      new QueueItem("Recent", vscode.TreeItemCollapsibleState.Expanded, {
        description: String(recentFinishedChildren.length),
        children: recentFinishedChildren.length ? recentFinishedChildren : [this.infoItem("No finished tasks yet", "Completed tasks will appear here.", "history")],
        iconPath: new vscode.ThemeIcon("history"),
      }),
    ];

    if (olderFinishedChildren.length) {
      queueChildren.push(
        new QueueItem("History", vscode.TreeItemCollapsibleState.Collapsed, {
          description: String(olderFinishedChildren.length),
          children: olderFinishedChildren,
          iconPath: new vscode.ThemeIcon("archive"),
        }),
      );
    }

    const eventChildren = this.recentEvents.length
      ? this.recentEvents.slice().reverse().map((event) => new QueueItem(buildEventLine(event), vscode.TreeItemCollapsibleState.None, {
          description: shortTime(event.timestamp),
          tooltip: JSON.stringify(event, null, 2),
          iconPath: new vscode.ThemeIcon(event.type === "task_failed" ? "error" : "history"),
        }))
      : [this.infoItem("No recent events", "Run an action to populate the event stream.", "history")];

    const fileChildren = this.recentFiles.length
      ? this.recentFiles.map((item) => new QueueItem(item.relative, vscode.TreeItemCollapsibleState.None, {
          description: `${item.kind} · ${shortTime(item.at)}`,
          tooltip: item.relative,
          iconPath: new vscode.ThemeIcon("file"),
        }))
      : [this.infoItem("No recent file changes", "Changes will appear here after the workspace updates.", "file")];

    return [
      new QueueItem("Current Execution", vscode.TreeItemCollapsibleState.Expanded, { children: executionChildren, iconPath: new vscode.ThemeIcon("debug-step-over") }),
      new QueueItem("Do Next", vscode.TreeItemCollapsibleState.Expanded, { children: nowChildren, iconPath: new vscode.ThemeIcon("compass") }),
      new QueueItem("Workspace Status", vscode.TreeItemCollapsibleState.Expanded, { children: summaryChildren, iconPath: new vscode.ThemeIcon("dashboard") }),
      new QueueItem("Task Queue", vscode.TreeItemCollapsibleState.Expanded, { description: String(this.queue.length), children: queueChildren, iconPath: new vscode.ThemeIcon("list-tree") }),
      new QueueItem("Workspace Details", vscode.TreeItemCollapsibleState.Collapsed, { children: detailChildren, iconPath: new vscode.ThemeIcon("info") }),
      new QueueItem("More Tools", vscode.TreeItemCollapsibleState.Collapsed, { children: toolChildren, iconPath: new vscode.ThemeIcon("tools") }),
      new QueueItem("Recent Events", vscode.TreeItemCollapsibleState.Collapsed, { description: String(this.recentEvents.length), children: eventChildren, iconPath: new vscode.ThemeIcon("history") }),
      new QueueItem("Recent Files", vscode.TreeItemCollapsibleState.Collapsed, { description: String(this.recentFiles.length), children: fileChildren, iconPath: new vscode.ThemeIcon("files") }),
    ];
  }

  getChildren(element) {
    if (element) {
      return element.children;
    }
    if (!this.workspaceRoot) {
      return [
        this.infoItem("No workspace open", "Open a local workspace to use Project Assistant.", "folder"),
      ];
    }
    if (!this.status) {
      return this.renderDisconnectedState();
    }
    return this.renderConnectedState();
  }

  async startDaemon() {
    if (!this.workspaceRoot) {
      vscode.window.showWarningMessage("Project Assistant: no local workspace is open.");
      return;
    }
    await this.runCommand("start daemon", async () => {
      const result = await this.runCli(["daemon", "start", this.workspaceRoot, "--json"]);
      this.output.appendLine(`daemon started: ${result.runtimeId}`);
      vscode.window.showInformationMessage("Project Assistant: background service started.");
      await this.refresh();
    });
  }

  async stopDaemon() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("stop daemon", async () => {
      await this.runCli(["daemon", "stop", this.workspaceRoot, "--json"]);
      this.output.appendLine("daemon stopping");
      setTimeout(() => this.refresh().catch((error) => this.output.appendLine(String(error))), 500);
    });
  }

  async manualContinue() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("open continue view", async () => {
      await this.openProjectAssistantModeAsMarkdown("continue", "continue.md");
    });
  }

  async oneClickContinue() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("queue continue snapshot", async () => {
      const task = await this.runCli(["daemon", "enqueue", "continue", this.workspaceRoot, "--json"]);
      this.output.appendLine(`queued continue: ${task.taskId}`);
      await this.refresh();
    });
  }

  async showProgress() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("queue progress snapshot", async () => {
      const task = await this.runCli(["daemon", "enqueue", "progress", this.workspaceRoot, "--json"]);
      this.output.appendLine(`queued progress: ${task.taskId}`);
      await this.refresh();
    });
  }

  async showHandoff() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("queue handoff snapshot", async () => {
      const task = await this.runCli(["daemon", "enqueue", "handoff", this.workspaceRoot, "--json"]);
      this.output.appendLine(`queued handoff: ${task.taskId}`);
      await this.refresh();
    });
  }

  async openProgressInTerminal() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("open progress view", async () => {
      await this.openProjectAssistantModeAsMarkdown("progress", "progress.md");
    });
  }

  async openHandoffInTerminal() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("open handoff view", async () => {
      await this.openProjectAssistantModeAsMarkdown("handoff", "handoff.md");
    });
  }

  async openRetrofitInTerminal() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("open retrofit view", async () => {
      await this.openProjectAssistantModeAsMarkdown("retrofit", "retrofit.md");
    });
  }

  async openProjectAssistantModeAsMarkdown(mode, fileName) {
    const targetPath = await this.renderProjectAssistantModeToFile(mode, fileName);
    const uri = vscode.Uri.file(targetPath);
    const document = await vscode.workspace.openTextDocument(uri);
    await vscode.window.showTextDocument(document, { preview: false, preserveFocus: false });
    await vscode.commands.executeCommand("markdown.showPreviewToSide", uri);
  }

  async renderProjectAssistantModeToFile(mode, fileName) {
    const output = await this.runCli([mode, this.workspaceRoot], false);
    const viewsDir = path.join(this.workspaceRoot, ".codex", "host-views");
    await fs.promises.mkdir(viewsDir, { recursive: true });
    const targetPath = path.join(viewsDir, fileName);
    await fs.promises.writeFile(targetPath, String(output), "utf8");
    return targetPath;
  }

  buildOpenAICodexConversationUri(conversationId) {
    return vscode.Uri.file(`/local/${conversationId}`).with({
      scheme: OPENAI_CODEX_SCHEME,
      authority: OPENAI_CODEX_AUTHORITY,
    });
  }

  async prepareCodexResumePack() {
    await this.refresh();
    const continuePath = await this.renderProjectAssistantModeToFile("continue", "continue.md");
    const progressPath = await this.renderProjectAssistantModeToFile("progress", "progress.md");
    const handoffPath = await this.renderProjectAssistantModeToFile("handoff", "handoff.md");
    const viewsDir = path.join(this.workspaceRoot, ".codex", "host-views");
    const packPath = path.join(viewsDir, "codex-resume-pack.md");
    const statusPath = path.join(this.workspaceRoot, ".codex", "status.md");
    const planPath = path.join(this.workspaceRoot, ".codex", "plan.md");
    const continuity = this.getExecutionContinuity();
    const files = [packPath, continuePath, handoffPath, progressPath, statusPath, planPath];
    const remainingTasks = continuity.remainingExecutionTasks.map((item) => `- ${item}`);
    const body = [
      "# Codex Resume Pack",
      "",
      `- Workspace: \`${markdownEscape(this.workspaceRoot)}\``,
      `- Ready to continue: \`${this.status && this.status.resumeReady ? "yes" : "not yet"}\``,
      `- Current stage: \`${markdownEscape(this.status && this.status.currentPhase ? this.status.currentPhase : "n/a")}\``,
      `- Current slice: \`${markdownEscape(this.status && this.status.activeSlice ? this.status.activeSlice : "n/a")}\``,
      `- Current checkpoint: \`${markdownEscape(continuity.currentCheckpoint)}\``,
      `- Next action: \`${markdownEscape(continuity.nextAction)}\``,
      `- Next action source: \`${markdownEscape(continuity.nextActionSource)}\``,
      `- Queue: \`${markdownEscape(countSummary(this.status && this.status.queueSummary ? this.status.queueSummary : {}))}\``,
      `- Recent session: \`${markdownEscape(this.workspaceSession ? `${this.workspaceSession.threadName} (${this.workspaceSession.id})` : "none")}\``,
      "",
      "## Continue Contract",
      "",
      "Read the attached resume pack files first, then continue the current active slice directly.",
      "",
      "Do not restart repo-wide discovery unless the durable control surface conflicts with itself.",
      "",
      "## Execution Continuity",
      "",
      `- Current checkpoint: \`${markdownEscape(continuity.currentCheckpoint)}\``,
      `- Next action: \`${markdownEscape(continuity.nextAction)}\``,
      "",
      "Treat that checkpoint as already-established truth and move straight into the next action.",
      "",
      "## Remaining Execution Tasks",
      "",
      ...(remainingTasks.length ? remainingTasks : ["- `(none captured)`"]),
      "",
      "Unless I explicitly say `做完手上工作停止`, keep going by default.",
      "",
      "## Attached Files",
      "",
      "- `codex-resume-pack.md`: this summary",
      "- `continue.md`: current execution line",
      "- `handoff.md`: resume pack and maintainer handoff",
      "- `progress.md`: maintainer dashboard snapshot",
      "- `.codex/status.md`: live execution truth",
      "- `.codex/plan.md`: live task plan",
      "",
      "## Suggested First Move",
      "",
      "1. Read `continue.md` and `.codex/status.md`.",
      `2. Continue from checkpoint: \`${markdownEscape(continuity.currentCheckpoint)}\`.`,
      `3. Start with next action: \`${markdownEscape(continuity.nextAction)}\`.`,
      "4. Continue implementation instead of asking for another manual resume prompt.",
      "",
    ].join("\n");
    await fs.promises.writeFile(packPath, body, "utf8");
    return files.filter((filePath) => fs.existsSync(filePath));
  }

  async prepareCodexAutoResumeArtifacts() {
    const resumeFiles = await this.prepareCodexResumePack();
    const viewsDir = path.join(this.workspaceRoot, ".codex", "host-views");
    const promptPath = path.join(viewsDir, "codex-auto-resume-prompt.md");
    const transportPath = path.join(viewsDir, "codex-auto-resume-transport.md");
    const workspaceName = this.getWorkspaceDisplayName();
    const workspaceRoot = this.workspaceRoot;
    const continuity = this.getExecutionContinuity();
    const sessionLabel = this.workspaceSession
      ? `${this.workspaceSession.threadName} (${this.workspaceSession.id})`
      : "未找到匹配的已保存会话，将启动新的 Codex 线程";
    const attachedNames = resumeFiles.map((filePath) => `- \`${markdownEscape(path.basename(filePath))}\``);
    const remainingTasks = continuity.remainingExecutionTasks.map((item) => `- ${item}`);
    const promptBody = [
      "# Codex 自动恢复提示",
      "",
      "这份提示由 Project Assistant VS Code 宿主自动生成。",
      "",
      "## 项目确认",
      "",
      `- 项目名：\`${markdownEscape(workspaceName)}\``,
      `- 工作区路径：\`${markdownEscape(workspaceRoot)}\``,
      `- 最近匹配会话：\`${markdownEscape(sessionLabel)}\``,
      "",
      "如果当前线程上下文和上面的项目信息不一致，优先以上面的工作区路径为准。",
      "",
      "## 当前任务",
      "",
      "先读取附加的 resume 文件，确认当前 active slice，然后直接继续这个仓库里的工作。",
      "",
      "不要重新从零做仓库总览；把下面这个 checkpoint 当成当前已知真相。",
      "",
      "## 当前连续性",
      "",
      `- 当前 checkpoint：\`${markdownEscape(continuity.currentCheckpoint)}\``,
      `- 下一动作：\`${markdownEscape(continuity.nextAction)}\``,
      `- 下一动作来源：\`${markdownEscape(continuity.nextActionSource)}\``,
      "",
      "收到这些恢复材料后，默认直接从“下一动作”切入，而不是重新开始一轮 resume 问答。",
      "",
      "## 剩余执行任务",
      "",
      ...(remainingTasks.length ? remainingTasks : ["- `(none captured)`"]),
      "",
      `除非我明确说 \`${STOP_AFTER_CURRENT_TEXT}\`，否则默认持续推进，不要停在“等下一句指令”。`,
      "",
      "## 附加文件",
      "",
      ...attachedNames,
      "",
      "## 恢复契约",
      "",
      "1. 先读 `codex-resume-pack.md`、`continue.md`、`.codex/status.md`。",
      "2. 把 `handoff.md`、`progress.md`、`.codex/plan.md` 当作辅助上下文。",
      "3. 优先从“下一动作”进入真实实现推进，不要先回到一轮新的 resume 问答。",
      "4. 不要把时间花在修改这个自动提交使用的 transport shim 文件上。",
      "",
      "## 正确项目校验",
      "",
      "1. 你当前要工作的 repo 就是上面这条 `工作区路径`。",
      "2. 任何修改、读取、验证，都以这个工作区为准。",
      "3. 如果你怀疑当前线程不是这个项目，先说明冲突，再按这个工作区继续。",
      "",
    ].join("\n");
    const transportComment = [
      `Project Assistant 自动恢复传输文件。目标项目: ${workspaceName} (${workspaceRoot})。`,
      "不要花时间编辑这个文件；它只用于从 VS Code 宿主自动提交一条 Codex 恢复请求。",
      "",
      "实际任务：",
      `- 目标项目是 ${workspaceName}，工作区路径是 ${workspaceRoot}。`,
      `- 当前 checkpoint 是 ${continuity.currentCheckpoint}。`,
      `- 下一动作是 ${continuity.nextAction}。`,
      "- 先读取附加的 resume 文件。",
      "- 不要重新从零做仓库扫描。",
      "- 直接从下一动作继续这个仓库里的工作。",
      `- 除非用户明确说 "${STOP_AFTER_CURRENT_TEXT}"，否则默认持续推进。`,
      "- 优先做真实 repo 改动，而不是修改这个传输文件。",
    ].join("\n");
    const transportBody = [
      "<!--",
      transportComment,
      "-->",
      "",
      "# Project Assistant 自动恢复传输文件",
      "",
      `- 目标项目：\`${markdownEscape(workspaceName)}\``,
      `- 工作区路径：\`${markdownEscape(workspaceRoot)}\``,
      "",
      "这个文件只是 VS Code 内 Codex 自动恢复使用的传输 shim。",
      "",
      "真正的恢复说明在 `codex-auto-resume-prompt.md` 和附加的 resume pack 文件里。",
      "",
    ].join("\n");
    await fs.promises.writeFile(promptPath, promptBody, "utf8");
    await fs.promises.writeFile(transportPath, transportBody, "utf8");
    return {
      promptBody,
      promptPath,
      resumeFiles,
      transportPath,
      transportComment,
    };
  }

  async attachFilesToCodexThread(filePaths) {
    for (const filePath of filePaths) {
      await vscode.commands.executeCommand("chatgpt.addFileToThread", vscode.Uri.file(filePath));
      await sleep(120);
    }
  }

  async runAppleScript(script) {
    return new Promise((resolve, reject) => {
      const child = cp.spawn("osascript", ["-"], { stdio: ["pipe", "pipe", "pipe"] });
      let stdout = "";
      let stderr = "";
      const timer = setTimeout(() => {
        child.kill("SIGTERM");
        reject(new Error("AppleScript timed out while trying to auto-submit the Codex resume prompt."));
      }, 15000);
      child.stdout.on("data", (chunk) => {
        stdout += chunk.toString();
      });
      child.stderr.on("data", (chunk) => {
        stderr += chunk.toString();
      });
      child.on("error", (error) => {
        clearTimeout(timer);
        reject(error);
      });
      child.on("close", (code) => {
        clearTimeout(timer);
        if (code === 0) {
          resolve(stdout.trim());
          return;
        }
        reject(new Error((stderr || stdout || `AppleScript exited with code ${code}`).trim()));
      });
      child.stdin.end(script);
    });
  }

  buildExactSessionAutoSubmitScript(promptPath) {
    const appName = appleScriptQuote(vscode.env.appName || "Visual Studio Code");
    const submitDelaySeconds = (this.getAutoResumeDelayMs() / 1000).toFixed(2);
    return [
      `set promptPath to POSIX file "${appleScriptQuote(promptPath)}"`,
      "set savedClipboard to the clipboard",
      "set promptText to read promptPath as «class utf8»",
      "set the clipboard to promptText",
      `tell application "${appName}" to activate`,
      `delay ${submitDelaySeconds}`,
      "tell application \"System Events\"",
      "  keystroke \"v\" using {command down}",
      "  delay 0.20",
      "  key code 36",
      "end tell",
      "delay 0.15",
      "try",
      "  set the clipboard to savedClipboard",
      "end try",
      "return \"submitted\"",
    ].join("\n");
  }

  async autoSubmitPromptIntoOpenedCodexSession(promptBody, triggerLabel) {
    if (!this.canAutoSubmitIntoExactSession()) {
      return false;
    }
    const viewsDir = path.join(this.workspaceRoot, ".codex", "host-views");
    const submitPath = path.join(viewsDir, "codex-exact-session-submit.md");
    await fs.promises.mkdir(viewsDir, { recursive: true });
    await fs.promises.writeFile(submitPath, promptBody, "utf8");
    this.output.appendLine(`exact-session auto-submit: ${triggerLabel} -> ${submitPath}`);
    await this.runAppleScript(this.buildExactSessionAutoSubmitScript(submitPath));
    return true;
  }

  async openWorkspaceSessionInCodex() {
    const uri = this.buildOpenAICodexConversationUri(this.workspaceSession.id);
    const viewColumn = vscode.window.activeTextEditor ? vscode.window.activeTextEditor.viewColumn : vscode.ViewColumn.Active;
    await vscode.commands.executeCommand("vscode.openWith", uri, OPENAI_CODEX_EDITOR_VIEW, {
      viewColumn,
      preserveFocus: false,
      preview: false,
    });
  }

  buildResumeCommand() {
    if (!this.workspaceRoot) {
      throw new Error("No workspace is open.");
    }
    const config = vscode.workspace.getConfiguration();
    const template = String(config.get("projectAssistant.resumeCommand", "") || "").trim();
    const codexPath = this.resolveCodexPath();
    const sessionId = this.workspaceSession ? this.workspaceSession.id : "";
    const threadName = this.workspaceSession ? this.workspaceSession.threadName : "";

    if (template) {
      const prompt = String(config.get("projectAssistant.resumePrompt", "项目助手 继续") || "").trim() || "项目助手 继续";
      return template
        .replaceAll("${workspace}", this.workspaceRoot)
        .replaceAll("${prompt}", prompt)
        .replaceAll("${codex}", codexPath)
        .replaceAll("${session_id}", sessionId)
        .replaceAll("${thread_name}", threadName);
    }

    if (sessionId) {
      return `${shellQuote(codexPath)} -C ${shellQuote(this.workspaceRoot)} resume ${sessionId}`;
    }

    return `${shellQuote(codexPath)} -C ${shellQuote(this.workspaceRoot)} resume`;
  }

  async openRecentCodexSession() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("open recent codex session", async () => {
      if (!this.workspaceSession) {
        vscode.window.showInformationMessage("Project Assistant: no saved Codex session was found for this workspace yet.");
        return;
      }
      if (await this.ensureOpenAICodexExtension()) {
        await this.openWorkspaceSessionInCodex();
        vscode.window.showInformationMessage(
          `Project Assistant: opened Codex session ${this.workspaceSession.id.slice(0, 8)} in VS Code.`,
        );
        return;
      }
      const viewsDir = path.join(this.workspaceRoot, ".codex", "host-views");
      await fs.promises.mkdir(viewsDir, { recursive: true });
      const targetPath = path.join(viewsDir, "recent-codex-session.md");
      const resumeCommand = this.buildResumeCommand();
      const body = [
        "# Recent Codex Session",
        "",
        `- Thread: \`${markdownEscape(this.workspaceSession.threadName)}\``,
        `- Session ID: \`${markdownEscape(this.workspaceSession.id)}\``,
        `- Updated: \`${markdownEscape(this.workspaceSession.updatedAt || "n/a")}\``,
        `- Workspace: \`${markdownEscape(this.workspaceSession.cwd)}\``,
        `- Source file: \`${markdownEscape(this.workspaceSession.sourceFile)}\``,
        "",
        "## Resume Behavior",
        "",
        "The VS Code Codex extension is not available, so resume falls back to the Codex CLI.",
        "",
        "```bash",
        resumeCommand,
        "```",
        "",
      ].join("\n");
      await fs.promises.writeFile(targetPath, body, "utf8");
      const uri = vscode.Uri.file(targetPath);
      const document = await vscode.workspace.openTextDocument(uri);
      await vscode.window.showTextDocument(document, { preview: false, preserveFocus: false });
      await vscode.commands.executeCommand("markdown.showPreviewToSide", uri);
    });
  }

  async resumeCodexInternal(options = {}) {
    if (!this.workspaceRoot) {
      return null;
    }
    if (this.status && !this.status.resumeReady) {
      this.output.appendLine("resume requested before daemon marked the workspace as resume-ready");
    }
    const codexExtension = await this.ensureOpenAICodexExtension();
    if (codexExtension) {
      const resumeFiles = await this.prepareCodexResumePack();
      if (this.workspaceSession) {
        const artifacts = await this.prepareCodexAutoResumeArtifacts();
        await this.openWorkspaceSessionInCodex();
        await sleep(400);
        await this.attachFilesToCodexThread(resumeFiles);
        const autoSubmitted = options.tryAutoSubmit
          ? await this.autoSubmitPromptIntoOpenedCodexSession(
              artifacts.promptBody,
              options.triggerSource || "manual resume",
            )
          : false;
        if (autoSubmitted) {
          if (!options.silentSuccess) {
            vscode.window.showInformationMessage(
              `Project Assistant: 已打开精确 Codex 会话 ${this.workspaceSession.id.slice(0, 8)}，附加了恢复材料，并自动发送了恢复提示。`,
            );
          }
          return { mode: "exact-session-auto-submit", autoSubmitted: true };
        }
        await vscode.env.clipboard.writeText(artifacts.promptBody);
        if (!options.silentSuccess) {
          const message = this.isExactSessionAutoSubmitEnabled()
            ? `Project Assistant: 已打开精确 Codex 会话 ${this.workspaceSession.id.slice(0, 8)}，附加了恢复材料；自动发送不可用，恢复提示已复制到剪贴板。`
            : `Project Assistant: 已打开精确 Codex 会话 ${this.workspaceSession.id.slice(0, 8)}，附加了恢复材料，并把恢复提示复制到了剪贴板。`;
          vscode.window.showInformationMessage(message);
        }
        return { mode: "exact-session-opened", autoSubmitted: false };
      }
      await vscode.commands.executeCommand("chatgpt.openSidebar");
      await vscode.commands.executeCommand("chatgpt.newChat");
      await sleep(400);
      await this.attachFilesToCodexThread(resumeFiles);
      if (!options.silentSuccess) {
        vscode.window.showWarningMessage(
          "Project Assistant: no exact saved session was found, so a new Codex thread was opened in VS Code with the current resume pack attached.",
        );
      }
      return { mode: "new-thread-opened", autoSubmitted: false };
    }
    if (!options.silentSuccess) {
      if (this.workspaceSession) {
        vscode.window.showInformationMessage(
          `Project Assistant: VS Code Codex extension not found, falling back to exact CLI session ${this.workspaceSession.id.slice(0, 8)} (${this.workspaceSession.threadName}).`,
        );
      } else {
        vscode.window.showWarningMessage(
          "Project Assistant: VS Code Codex extension not found, falling back to Codex CLI resume in this workspace.",
        );
      }
    }
    const terminal = vscode.window.createTerminal("Project Assistant Resume Codex");
    terminal.show();
    terminal.sendText(this.buildResumeCommand(), true);
    return { mode: "cli", autoSubmitted: false };
  }

  async resumeCodex() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("resume codex", async () => this.resumeCodexInternal({
      tryAutoSubmit: this.canAutoSubmitIntoExactSession(),
      triggerSource: "manual resume",
    }));
  }

  async autoResumeCodexInternal(options = {}) {
    if (!this.workspaceRoot) {
      return null;
    }
    const codexExtension = await this.ensureOpenAICodexExtension();
    if (!codexExtension) {
      if (!options.silentSuccess) {
        vscode.window.showWarningMessage(
          "Project Assistant: the Codex VS Code extension is not available, so auto-submit cannot run inside VS Code.",
        );
      }
      return null;
    }
    const artifacts = await this.prepareCodexAutoResumeArtifacts();
    await vscode.commands.executeCommand("chatgpt.openSidebar");
    await vscode.commands.executeCommand("chatgpt.implementTodo", {
      fileName: artifacts.transportPath,
      line: 1,
      comment: artifacts.transportComment,
    });
    await sleep(CODEX_AUTO_RESUME_ATTACH_DELAY_MS);
    await this.attachFilesToCodexThread([artifacts.promptPath, ...artifacts.resumeFiles]);
    if (!options.silentSuccess) {
      vscode.window.showInformationMessage(
        `Project Assistant: 已为 ${this.getWorkspaceDisplayName()} 启动新的 Codex 自动恢复线程，并自动提交恢复请求。`,
      );
    }
    return { mode: "new-thread-auto-submit", autoSubmitted: true };
  }

  async autoResumeCodex() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("auto resume codex", async () => this.autoResumeCodexInternal({
      triggerSource: "manual auto-resume",
    }));
  }

  async startAutoCoding() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("start auto coding", async () => {
      await this.refresh();
      const continuity = this.getExecutionContinuity();
      if (!this.hasActionablePlan(continuity)) {
        this.autoCodingMode = AUTO_CODING_OFF;
        this.persistAutoCodingState();
        await this.openPlanDoc();
        vscode.window.showInformationMessage(
          "Project Assistant: 暂时没有新的可执行任务。我会按 .codex/plan.md / .codex/status.md 工作；先补齐规划文档，再开启 Auto Coding。",
        );
        return;
      }
      this.autoCodingMode = AUTO_CODING_ON;
      this.persistAutoCodingState();
      await this.updateViewContexts();
      this._onDidChangeTreeData.fire();
      const counts = this.status && this.status.queueSummary ? this.status.queueSummary : {};
      if (!this.status || !this.status.resumeReady || (counts.queued || 0) > 0 || (counts.running || 0) > 0) {
        vscode.window.showInformationMessage(
          `Project Assistant: Auto Coding 已开启。当前会按 ${continuity.nextAction} 持续推进；一旦 workspace ready，就会自动继续。`,
        );
        return;
      }
      const strategy = this.getAutoResumeStrategy();
      if (strategy === "new-thread") {
        const result = await this.autoResumeCodexInternal({
          triggerSource: "manual auto coding start",
          silentSuccess: true,
        });
        this.recordAutoResumeOutcome({
          status: "succeeded",
          label: `Auto Coding started -> ${continuity.nextAction}`,
          triggerId: this.lastEventId,
          triggerType: "manual-auto-coding-start",
          mode: result ? result.mode : "new-thread-auto-submit",
        });
        vscode.window.showInformationMessage(
          `Project Assistant: Auto Coding 已开启，并已开始按 ${continuity.nextAction} 自动推进。`,
        );
        return;
      }
      if (this.canAutoResumeIntoExactSession()) {
        const result = await this.resumeCodexInternal({
          tryAutoSubmit: true,
          triggerSource: "manual auto coding start",
          silentSuccess: true,
        });
        if (result && result.autoSubmitted) {
          this.recordAutoResumeOutcome({
            status: "succeeded",
            label: `Auto Coding started -> ${continuity.nextAction}`,
            triggerId: this.lastEventId,
            triggerType: "manual-auto-coding-start",
            mode: result.mode,
          });
          vscode.window.showInformationMessage(
            `Project Assistant: Auto Coding 已开启，并已开始按 ${continuity.nextAction} 自动推进。`,
          );
          return;
        }
      }
      if (this.shouldAutoResumeFallbackToNewThread()) {
        const fallback = await this.autoResumeCodexInternal({
          triggerSource: "manual auto coding start fallback",
          silentSuccess: true,
        });
        this.recordAutoResumeOutcome({
          status: "succeeded",
          label: `Auto Coding started with fallback -> ${continuity.nextAction}`,
          triggerId: this.lastEventId,
          triggerType: "manual-auto-coding-start",
          mode: fallback ? fallback.mode : "new-thread-auto-submit",
        });
        vscode.window.showInformationMessage(
          `Project Assistant: Auto Coding 已开启。精确会话自动发送不可用，已回退到新的 Codex 线程并开始按 ${continuity.nextAction} 推进。`,
        );
        return;
      }
      this.recordAutoResumeOutcome({
        status: "skipped",
        label: "Auto Coding waiting for auto-send support",
        reason: "exact-session auto-send unavailable",
        triggerId: this.lastEventId,
        triggerType: "manual-auto-coding-start",
      });
      vscode.window.showWarningMessage(
        `Project Assistant: Auto Coding 已开启，但当前还不能自动发送到精确会话。恢复提示已准备好，下一动作是 ${continuity.nextAction}。`,
      );
    });
  }

  async stopAutoCoding() {
    if (!this.workspaceRoot) {
      return;
    }
    await this.runCommand("stop auto coding", async () => {
      await this.refresh();
      const shouldDrainCurrentTurn = Boolean(this.autoResumeInFlight || (this.status && this.status.foregroundLease));
      this.autoCodingMode = shouldDrainCurrentTurn ? AUTO_CODING_STOP_AFTER_CURRENT : AUTO_CODING_OFF;
      this.persistAutoCodingState();
      await this.updateViewContexts();
      this._onDidChangeTreeData.fire();
      if (shouldDrainCurrentTurn) {
        vscode.window.showInformationMessage("Project Assistant: Auto Coding 会在当前一轮完成后停止。");
        return;
      }
      vscode.window.showInformationMessage("Project Assistant: Auto Coding 已关闭，当前回到手动模式。");
    });
  }

  async maybeAutoResumeFromDaemonEvents(events) {
    if (!this.workspaceRoot || !this.status || !Array.isArray(events) || !events.length) {
      return;
    }
    if (!this.isAutoCodingEnabled() || this.autoResumeInFlight) {
      return;
    }
    const counts = this.status.queueSummary || {};
    if (!this.status.resumeReady || (counts.queued || 0) > 0 || (counts.running || 0) > 0) {
      return;
    }
    const triggerEvent = events
      .filter((event) => ["task_completed", "resume_ready", "session_stopped"].includes(event.type))
      .sort((a, b) => Number(a.id || 0) - Number(b.id || 0))
      .pop();
    if (!triggerEvent) {
      return;
    }
    const triggerId = Number(triggerEvent.id || 0);
    if (!Number.isFinite(triggerId) || triggerId <= this.lastAutoResumeTriggerId) {
      return;
    }
    const triggerTypes = new Set(events.map((event) => event.type));
    if (triggerTypes.has("resume_ready") || triggerTypes.has("task_completed") || triggerTypes.has("session_stopped")) {
      try {
        this.status = await this.runCli(["daemon", "status", this.workspaceRoot, "--json"]);
        const queuePayload = await this.runCli(["queue", this.workspaceRoot, "--json"]);
        this.queue = queuePayload.tasks || [];
      } catch (error) {
        this.output.appendLine(`auto-resume refresh failed before handling event ${triggerId}: ${String(error && error.message ? error.message : error)}`);
      }
    }
    const lastAttemptAtMs = this.lastAutoResumeAttemptAt ? Date.parse(this.lastAutoResumeAttemptAt) : 0;
    const cooldownMs = this.getAutoResumeCooldownMs();
    if (lastAttemptAtMs && Number.isFinite(lastAttemptAtMs) && (Date.now() - lastAttemptAtMs) < cooldownMs) {
      this.recordAutoResumeOutcome({
        status: "skipped",
        label: "Skipped during cooldown",
        reason: `cooldown ${cooldownMs}ms`,
        triggerId,
        triggerType: triggerEvent.type,
      });
      this.output.appendLine(`auto-resume skipped: cooldown active for event ${triggerId}`);
      return;
    }
    this.lastAutoResumeTriggerId = triggerId;
    this.persistAutoResumeState();
    this.autoResumeInFlight = true;
    try {
      const strategy = this.getAutoResumeStrategy();
      const continuity = this.getExecutionContinuity();
      this.output.appendLine(`auto-resume trigger: event ${triggerId} (${triggerEvent.type}) using strategy ${strategy}`);
      if (strategy === "new-thread") {
        const result = await this.autoResumeCodexInternal({
          triggerSource: `daemon event ${triggerId}`,
          silentSuccess: true,
        });
        this.recordAutoResumeOutcome({
          status: "succeeded",
          label: `Started new auto-resume thread -> ${continuity.nextAction}`,
          triggerId,
          triggerType: triggerEvent.type,
          mode: result ? result.mode : "new-thread-auto-submit",
        });
        vscode.window.showInformationMessage(
          `Project Assistant: daemon 完成后已为 ${this.getWorkspaceDisplayName()} 自动启动新的 Codex 恢复线程，下一动作是 ${continuity.nextAction}。`,
        );
        return;
      }
      if (this.canAutoResumeIntoExactSession()) {
        const result = await this.resumeCodexInternal({
          tryAutoSubmit: true,
          triggerSource: `daemon event ${triggerId}`,
          silentSuccess: true,
        });
        if (result && result.autoSubmitted) {
          this.recordAutoResumeOutcome({
            status: "succeeded",
            label: `Continued exact session ${shortId(this.workspaceSession && this.workspaceSession.id)} -> ${continuity.nextAction}`,
            triggerId,
            triggerType: triggerEvent.type,
            mode: result.mode,
          });
          vscode.window.showInformationMessage(
            `Project Assistant: daemon 完成后已在精确 Codex 会话里自动继续 ${this.getWorkspaceDisplayName()}，下一动作是 ${continuity.nextAction}。`,
          );
          return;
        }
      }
      if (this.shouldAutoResumeFallbackToNewThread()) {
        const fallback = await this.autoResumeCodexInternal({
          triggerSource: `daemon event ${triggerId} fallback`,
          silentSuccess: true,
        });
        this.recordAutoResumeOutcome({
          status: "succeeded",
          label: `Fell back to new auto-resume thread -> ${continuity.nextAction}`,
          triggerId,
          triggerType: triggerEvent.type,
          mode: fallback ? fallback.mode : "new-thread-auto-submit",
        });
        vscode.window.showInformationMessage(
          `Project Assistant: 精确会话自动继续不可用，已为 ${this.getWorkspaceDisplayName()} 自动回退到新的 Codex 恢复线程，下一动作是 ${continuity.nextAction}。`,
        );
        return;
      }
      this.recordAutoResumeOutcome({
        status: "skipped",
        label: "Waiting for exact-session auto-send",
        reason: "exact-session auto-send unavailable",
        triggerId,
        triggerType: triggerEvent.type,
      });
      this.output.appendLine("auto-resume skipped: exact-session auto-send is not available in the current environment");
    } catch (error) {
      const message = String(error && error.message ? error.message : error);
      this.recordAutoResumeOutcome({
        status: "failed",
        label: "Automatic resume failed",
        reason: message,
        triggerId,
        triggerType: triggerEvent.type,
      });
      this.output.appendLine(`auto-resume failed: ${message}`);
      vscode.window.showWarningMessage(`Project Assistant: 自动继续失败，原因是 ${message}`);
    } finally {
      this.autoResumeInFlight = false;
      if (this.isAutoCodingStoppingAfterCurrent()) {
        this.autoCodingMode = AUTO_CODING_OFF;
        this.persistAutoCodingState();
        await this.updateViewContexts();
      }
      this._onDidChangeTreeData.fire();
    }
  }

  async configureCliPath() {
    await vscode.commands.executeCommand("workbench.action.openSettings", "projectAssistant.cliPath");
  }

  async openWorkspaceMarkdownFile(relativePath) {
    if (!this.workspaceRoot) {
      return;
    }
    const targetPath = path.join(this.workspaceRoot, relativePath);
    try {
      await fs.promises.access(targetPath, fs.constants.F_OK);
    } catch {
      vscode.window.showWarningMessage(`Project Assistant: ${relativePath} does not exist in this workspace yet.`);
      return;
    }
    const uri = vscode.Uri.file(targetPath);
    const document = await vscode.workspace.openTextDocument(uri);
    await vscode.window.showTextDocument(document, { preview: false, preserveFocus: false });
    if (relativePath.endsWith(".md")) {
      await vscode.commands.executeCommand("markdown.showPreviewToSide", uri);
    }
  }

  async openStatusDoc() {
    await this.openWorkspaceMarkdownFile(path.join(".codex", "status.md"));
  }

  async openPlanDoc() {
    await this.openWorkspaceMarkdownFile(path.join(".codex", "plan.md"));
  }

  async openNextActionSource() {
    const basis = this.getNextActionBasis();
    await this.openWorkspaceMarkdownFile(basis.primaryDoc);
  }

  async reloadWindow() {
    await vscode.commands.executeCommand("workbench.action.reloadWindow");
  }

  async copyStopInstruction() {
    await vscode.env.clipboard.writeText(STOP_AFTER_CURRENT_TEXT);
    vscode.window.showInformationMessage(`Copied stop instruction: ${STOP_AFTER_CURRENT_TEXT}`);
  }

  showOutput() {
    this.output.show(true);
  }

  async openTaskLog(task) {
    if (!task || !task.outputPath) {
      return;
    }
    const uri = vscode.Uri.file(task.outputPath);
    const doc = await vscode.workspace.openTextDocument(uri);
    await vscode.window.showTextDocument(doc, { preview: false });
  }
}

function activate(context) {
  const output = vscode.window.createOutputChannel("Project Assistant Host");
  const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  const provider = new ProjectAssistantProvider(context.extensionPath, output, statusBar, context.workspaceState);

  context.subscriptions.push(
    output,
    statusBar,
    vscode.window.registerTreeDataProvider("projectAssistantQueue", provider),
    vscode.commands.registerCommand("projectAssistant.startDaemon", () => provider.startDaemon()),
    vscode.commands.registerCommand("projectAssistant.stopDaemon", () => provider.stopDaemon()),
    vscode.commands.registerCommand("projectAssistant.refresh", () => provider.refresh()),
    vscode.commands.registerCommand("projectAssistant.reloadWindow", () => provider.reloadWindow()),
    vscode.commands.registerCommand("projectAssistant.startAutoCoding", () => provider.startAutoCoding()),
    vscode.commands.registerCommand("projectAssistant.stopAutoCoding", () => provider.stopAutoCoding()),
    vscode.commands.registerCommand("projectAssistant.openStatusDoc", () => provider.openStatusDoc()),
    vscode.commands.registerCommand("projectAssistant.openPlanDoc", () => provider.openPlanDoc()),
    vscode.commands.registerCommand("projectAssistant.openNextActionSource", () => provider.openNextActionSource()),
    vscode.commands.registerCommand("projectAssistant.manualContinue", () => provider.manualContinue()),
    vscode.commands.registerCommand("projectAssistant.oneClickContinue", () => provider.oneClickContinue()),
    vscode.commands.registerCommand("projectAssistant.showProgress", () => provider.showProgress()),
    vscode.commands.registerCommand("projectAssistant.showHandoff", () => provider.showHandoff()),
    vscode.commands.registerCommand("projectAssistant.resumeCodex", () => provider.resumeCodex()),
    vscode.commands.registerCommand("projectAssistant.autoResumeCodex", () => provider.autoResumeCodex()),
    vscode.commands.registerCommand("projectAssistant.openRecentCodexSession", () => provider.openRecentCodexSession()),
    vscode.commands.registerCommand("projectAssistant.openProgressInTerminal", () => provider.openProgressInTerminal()),
    vscode.commands.registerCommand("projectAssistant.openHandoffInTerminal", () => provider.openHandoffInTerminal()),
    vscode.commands.registerCommand("projectAssistant.openRetrofitInTerminal", () => provider.openRetrofitInTerminal()),
    vscode.commands.registerCommand("projectAssistant.configureCliPath", () => provider.configureCliPath()),
    vscode.commands.registerCommand("projectAssistant.copyStopInstruction", () => provider.copyStopInstruction()),
    vscode.commands.registerCommand("projectAssistant.showOutput", () => provider.showOutput()),
    vscode.commands.registerCommand("projectAssistant.openTaskLog", (task) => provider.openTaskLog(task)),
  );

  provider.activate(context);

  if (vscode.workspace.getConfiguration().get("projectAssistant.autoStartDaemon", false)) {
    provider.startDaemon().catch((error) => output.appendLine(String(error)));
  }
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
