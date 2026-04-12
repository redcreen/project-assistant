#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${PROJECT_ASSISTANT_REPO:-https://github.com/redcreen/project-assistant.git}"
REF="${PROJECT_ASSISTANT_REF:-v0.1.3}"
TARGET_DIR="${PROJECT_ASSISTANT_DIR:-$HOME/.codex/skills/project-assistant}"
BIN_DIR="${PROJECT_ASSISTANT_BIN_DIR:-$HOME/.local/bin}"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "Installing project-assistant from ${REPO_URL} @ ${REF}"

git clone --depth 1 "$REPO_URL" "$TMP_DIR/repo"
git -C "$TMP_DIR/repo" fetch --depth 1 origin "refs/tags/$REF:refs/tags/$REF"
git -C "$TMP_DIR/repo" checkout --detach "$REF"
mkdir -p "$(dirname "$TARGET_DIR")"
rm -rf "$TARGET_DIR"
cp -R "$TMP_DIR/repo" "$TARGET_DIR"
rm -rf "$TARGET_DIR/.git"
mkdir -p "$BIN_DIR"
chmod +x "$TARGET_DIR/bin/project-assistant"
ln -sfn "$TARGET_DIR/bin/project-assistant" "$BIN_DIR/project-assistant"

echo "Installed to $TARGET_DIR"
echo "CLI installed to $BIN_DIR/project-assistant"
echo "Next step: start a new Codex session, then run: 项目助手 菜单"
echo "Shell front door: project-assistant continue /path/to/repo"
