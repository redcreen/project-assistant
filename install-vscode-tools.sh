#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${PROJECT_ASSISTANT_REPO:-https://github.com/redcreen/project-assistant.git}"
REF="${PROJECT_ASSISTANT_REF:-v0.1.5}"
EXTENSIONS_DIR="${PROJECT_ASSISTANT_VSCODE_EXTENSIONS_DIR:-$HOME/.vscode/extensions}"
COMPONENTS_RAW="${PROJECT_ASSISTANT_VSCODE_COMPONENTS:-project-assistant-host workspace-doc-browser}"
SOURCE_DIR="${PROJECT_ASSISTANT_VSCODE_SOURCE_DIR:-}"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

normalize_components() {
  local raw normalized item
  raw="${1//,/ }"
  normalized=""
  for item in $raw; do
    case "$item" in
      all)
        normalized="$normalized project-assistant-host workspace-doc-browser"
        ;;
      host|project-assistant-host)
        normalized="$normalized project-assistant-host"
        ;;
      docs|doc-browser|workspace-doc-browser)
        normalized="$normalized workspace-doc-browser"
        ;;
      *)
        echo "Unsupported PROJECT_ASSISTANT_VSCODE_COMPONENTS item: $item" >&2
        exit 1
        ;;
    esac
  done
  printf '%s\n' "$normalized" | awk '{$1=$1; print}'
}

package_dir_for_component() {
  case "$1" in
    project-assistant-host)
      printf '%s\n' "integrations/vscode-host"
      ;;
    workspace-doc-browser)
      printf '%s\n' "integrations/workspace-doc-browser"
      ;;
    *)
      echo "Unknown component: $1" >&2
      exit 1
      ;;
  esac
}

read_package_field() {
  local package_json="$1"
  local field="$2"
  python3 - "$package_json" "$field" <<'PY'
import json
import sys
from pathlib import Path

package_json = Path(sys.argv[1])
field = sys.argv[2]
payload = json.loads(package_json.read_text(encoding="utf-8"))
print(payload[field])
PY
}

if [ -n "$SOURCE_DIR" ]; then
  SOURCE_DIR="$(cd "$SOURCE_DIR" && pwd)"
  if [ ! -f "$SOURCE_DIR/install-vscode-tools.sh" ]; then
    echo "PROJECT_ASSISTANT_VSCODE_SOURCE_DIR does not look like a project-assistant checkout: $SOURCE_DIR" >&2
    exit 1
  fi
  REPO_DIR="$SOURCE_DIR"
  echo "Installing VS Code tools from local source ${REPO_DIR}"
else
  echo "Installing VS Code tools from ${REPO_URL} @ ${REF}"
  REPO_DIR="$TMP_DIR/repo"
  git clone --depth 1 "$REPO_URL" "$REPO_DIR"
  git -C "$REPO_DIR" fetch --depth 1 origin "$REF"
  git -C "$REPO_DIR" checkout --detach FETCH_HEAD >/dev/null
fi

mkdir -p "$EXTENSIONS_DIR"
COMPONENTS="$(normalize_components "$COMPONENTS_RAW")"

for component in $COMPONENTS; do
  package_dir="$(package_dir_for_component "$component")"
  package_json="$REPO_DIR/$package_dir/package.json"
  publisher="$(read_package_field "$package_json" publisher)"
  name="$(read_package_field "$package_json" name)"
  version="$(read_package_field "$package_json" version)"
  extension_id="${publisher}.${name}"
  target_dir="${EXTENSIONS_DIR}/${extension_id}-${version}"

  shopt -s nullglob
  for old_dir in "${EXTENSIONS_DIR}/${extension_id}-"*; do
    rm -rf "$old_dir"
  done
  shopt -u nullglob

  mkdir -p "$target_dir"
  cp -R "$REPO_DIR/$package_dir/." "$target_dir/"
  echo "Installed ${extension_id} -> ${target_dir}"
done

if printf '%s\n' "$COMPONENTS" | grep -q "workspace-doc-browser" && ! command -v mkdocs >/dev/null 2>&1; then
  echo "Warning: Workspace Doc Browser requires mkdocs on your PATH." >&2
fi

echo "Next step: in VS Code run 'Developer: Restart Extension Host'"
echo "Installed components: ${COMPONENTS}"
