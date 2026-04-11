#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${PROJECT_ASSISTANT_REPO:-https://github.com/redcreen/project-assistant.git}"
REF="${PROJECT_ASSISTANT_REF:-v0.1.0}"
TARGET_DIR="${PROJECT_ASSISTANT_DIR:-$HOME/.codex/skills/project-assistant}"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "Installing project-assistant from ${REPO_URL} @ ${REF}"

git clone --depth 1 --branch "$REF" "$REPO_URL" "$TMP_DIR/repo"
mkdir -p "$(dirname "$TARGET_DIR")"
rm -rf "$TARGET_DIR"
cp -R "$TMP_DIR/repo" "$TARGET_DIR"
rm -rf "$TARGET_DIR/.git"

echo "Installed to $TARGET_DIR"
echo "Next step: start a new Codex session, then run: 项目助手 菜单"
