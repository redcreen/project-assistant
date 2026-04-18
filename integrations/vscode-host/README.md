# Project Assistant VS Code Host

This extension is the first host frontend for the `project-assistant` PTL daemon runtime.

## Install

One-line install from the stable tag:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.6/install-vscode-tools.sh | PROJECT_ASSISTANT_VSCODE_COMPONENTS=project-assistant-host bash
```

Install from the current checkout:

```bash
PROJECT_ASSISTANT_VSCODE_COMPONENTS=project-assistant-host bash install-vscode-tools.sh
```

Then in VS Code run:

```text
Developer: Restart Extension Host
```

## Quick Start

1. Open a local workspace.
2. Open the `Project Assistant` sidebar.
3. If the host cannot find the CLI, set `projectAssistant.cliPath` to the `bin/project-assistant` wrapper.
4. Click `Start background service`.
5. Turn `Auto Coding` on when you want the host to keep resuming the next planned step automatically.
6. Use `Resume last Codex session`, `Start new auto resume thread`, `Open continue view`, or the snapshot queue actions from the sidebar when you want a manual action.

## What You Will See

- `Workspace Status`: whether the daemon is running, whether the repo is ready to continue, the current phase/slice, and queue counts
- `Workspace Status` also shows `Current checkpoint` and `Next action`, derived from `.codex/status.md` and `.codex/plan.md` through the daemon status snapshot
- `Workspace Status` also shows `Auto coding`, which is the primary user-facing switch for “keep going until I explicitly stop”
- `Workspace Status` also shows the most recent Codex session detected for this workspace, and you can click it to open that session directly in VS Code when the Codex extension is installed
- `Workspace Status` also shows `Resume automation` and `Auto-resume monitor`, so you can see whether exact-session auto-send and daemon-triggered auto-resume are active
- `Workspace Status` also shows `Last auto-resume`, so you can see whether the most recent daemon-triggered resume attempt succeeded, skipped, or failed
- `Quick Actions`: start/stop the daemon, resume Codex, open a continue snapshot, or queue progress/handoff snapshots
- `Quick Actions` also includes `Start auto coding` and `Stop auto coding`
- `Quick Actions` also includes `Start new auto resume thread`, which opens a fresh Codex thread and auto-submits a generated Project Assistant resume request
- `Project Assistant Commands`: open the main `continue / progress / handoff / retrofit` flows directly from the sidebar
- `Quick Actions` also includes a one-click copy action for `做完手上工作停止`
- `Suggested Next Step`: a short, state-driven recommendation block above the queue
- `Task Queue`: background tasks with live status and clickable logs
- `Recent Events`: daemon lifecycle and task events
- `Recent Files`: recent workspace changes, excluding `.git`, `node_modules`, and daemon runtime files

## What It Does

- shows daemon queue and live status in the VS Code activity bar
- shows a Status Bar summary for daemon state and resume readiness
- streams daemon events into an Output channel
- provides an `Auto Coding` switch that turns daemon-driven automatic continuation on or off per workspace
- provides a `Resume Last Codex Session` action that prefers opening the matching Codex session directly in VS Code
- can experimentally auto-send the generated resume prompt into that exact saved session on local macOS when `projectAssistant.experimentalExactSessionAutoSubmit` is enabled
- provides a `Start New Auto Resume Thread` action that uses the Codex extension's public `Implement Todo` bridge to auto-submit a generated resume request in a fresh Codex thread
- when `Auto Coding` is on, the host watches daemon `resume-ready / task_completed / session_stopped` events and auto-launches the configured resume path
- persists the last daemon-triggered auto-resume trigger id and outcome per workspace, so reloads do not repeatedly replay the same background resume
- provides an `Open Recent Codex Session` action and clickable session row
- opens `continue / progress / handoff / retrofit` outputs as Markdown files and preview panes
- provides queued `continue / progress / handoff` snapshot actions

## What It Does Not Do

- it does not rely on a documented public Codex API for exact-session message submission; the exact-session auto-send path is currently an experimental local host bridge
- it does not claim control over another participant's existing chat session outside the current workspace-safe resume flow
- it does not require web or remote host support in v1

## Important Behavior Notes

- `Resume Last Codex Session` first looks for the latest saved Codex session whose recorded `cwd` matches the current workspace.
- If the OpenAI Codex VS Code extension is installed and a matching session is found, the host opens that exact session in a VS Code Codex panel and attaches the latest resume pack files.
- If `projectAssistant.experimentalExactSessionAutoSubmit` is enabled on local macOS, `Resume Last Codex Session` will then try to paste and send the generated resume prompt into that exact session automatically.
- If exact-session auto-send is disabled or unavailable, the host falls back to copying the generated prompt to the clipboard after opening the session.
- If the OpenAI Codex VS Code extension is installed but no matching session is found, the host opens a new Codex thread in the sidebar and attaches the latest resume pack files.
- `Start New Auto Resume Thread` is different from `Resume Last Codex Session`: it always starts a fresh Codex thread and auto-submits a generated resume request through the public `chatgpt.implementTodo` command.
- `Start New Auto Resume Thread` is experimental. It does not inject text into the exact existing session; it uses a transport shim file and then attaches the generated resume pack files.
- `Start auto coding` is the primary workflow switch. If there is no durable next action in `.codex/plan.md` or `.codex/status.md`, the host opens the plan and tells you to plan first.
- If `Auto Coding` is on, daemon completion and `resume-ready` events can automatically launch another Codex turn.
- `Stop auto coding` does not interrupt the current turn; it lets the current work settle and then returns the workspace to manual mode.
- `projectAssistant.autoResumeStrategy = exact-session` depends on the same exact-session auto-send bridge. If that bridge is unavailable, the host logs the trigger and waits instead of guessing a different path.
- `projectAssistant.autoResumeStrategy = new-thread` uses the fresh-thread auto-submit bridge and does not depend on exact-session auto-send.
- `projectAssistant.autoResumeFallbackToNewThread = true` lets the host fall back from exact-session auto-resume to a fresh auto-resume thread when the exact-session bridge is unavailable.
- `projectAssistant.autoResumeCooldownMs` prevents rapid daemon event bursts from launching repeated automatic resume attempts.
- If the OpenAI Codex VS Code extension is not installed, the host falls back to the Codex CLI for resume.
- `Workspace Status -> Resume target` tells you whether resume will open an exact VS Code session, a new VS Code thread, or a CLI fallback path.
- `Queue Continue Snapshot` does not resume a coding session by itself; it queues a background `continue` snapshot task.
- `Open Continue View`, `Open Progress View`, and similar actions write Markdown files into `.codex/host-views/` and open the preview in VS Code.
- `Resume Last Codex Session` writes a `codex-resume-pack.md` file into `.codex/host-views/` and attaches it, along with `continue / handoff / progress / status / plan`, to the Codex thread when the VS Code bridge is active.
- The generated resume pack and auto-resume prompt now carry `current checkpoint -> next action` continuity so Codex can move straight into the next step instead of redoing repo-wide discovery.
- `Start New Auto Resume Thread` also writes `codex-auto-resume-prompt.md` and `codex-auto-resume-transport.md` into `.codex/host-views/`.
- `Open Recent Codex Session` opens the exact saved session in VS Code when possible, and only falls back to `.codex/host-views/recent-codex-session.md` when the Codex extension is unavailable.
- The host assumes a “keep going until explicitly stopped” workflow; `Copy Stop Instruction` copies the exact phrase used to stop after the current work.

## Default CLI Resolution

If `projectAssistant.cliPath` is empty, the extension tries these locations in order:

- `<workspace>/bin/project-assistant`
- `<extension>/bin/project-assistant` and nearby parent `bin/` folders
- `~/.codex/skills/project-assistant/bin/project-assistant`
- `project-assistant` on `PATH`

## Resume Configuration

- `projectAssistant.codexPath`: optional explicit path to the Codex CLI
- `projectAssistant.resumeCommand`: optional custom command template for resume actions
- `projectAssistant.resumePrompt`: prompt placeholder used only by custom resume commands
- `projectAssistant.experimentalExactSessionAutoSubmit`: enable the experimental macOS bridge that tries to auto-send the generated resume prompt into the exact reopened Codex session
- `projectAssistant.autoResumeOnReady`: low-level compatibility flag kept for older setups; user-facing control should go through the `Auto Coding` switch
- `projectAssistant.autoResumeStrategy`: choose `new-thread` or `exact-session` for Auto Coding resume attempts; `new-thread` is the safer default because it keeps automatic resumes isolated per workspace
- `projectAssistant.autoResumeFallbackToNewThread`: when exact-session auto-send is unavailable, allow Auto Coding to fall back to a fresh Codex thread
- `projectAssistant.experimentalAutoResumeIntoExactSession`: extra safety override for daemon-driven auto-resume; keep this off unless you explicitly accept the risk of automatic exact-session targeting
- `projectAssistant.autoResumeDelayMs`: delay before the host pastes and sends the generated prompt into an opened Codex session
- `projectAssistant.autoResumeCooldownMs`: minimum interval between daemon-triggered automatic resume attempts
