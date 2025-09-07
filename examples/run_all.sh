#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$ROOT_DIR/.." && pwd)"

# Load .env from repo root if present
if [[ -f "$REPO_ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$REPO_ROOT/.env"
  set +a
fi

if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  echo "[ERROR] DEEPSEEK_API_KEY is not set. Please export it or add to .env before running examples." >&2
  echo "export DEEPSEEK_API_KEY=\"your-key\"" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "[ERROR] 'uv' is not installed. Install from https://docs.astral.sh/uv/getting-started/" >&2
  exit 1
fi

echo "Syncing environment with uv (this may take a moment)..."
(
  cd "$REPO_ROOT" && uv sync --no-dev
) || { echo "[ERROR] uv sync failed" >&2; exit 1; }

echo "Running all examples under: $ROOT_DIR using uv run"
echo

passed=()
failed=()

for dir in "$ROOT_DIR"/*; do
  [[ -d "$dir" ]] || continue
  [[ -f "$dir/main.py" ]] || continue

  name="$(basename "$dir")"
  echo "===== Running: $name ====="
  (
    cd "$REPO_ROOT" && uv run -q python "examples/$name/main.py"
  ) && {
    echo "[OK] $name"; passed+=("$name");
  } || {
    echo "[FAIL] $name"; failed+=("$name");
  }
  echo
done

echo "Summary:"
echo "  Passed: ${#passed[@]} -> ${passed[*]:-}" 
echo "  Failed: ${#failed[@]} -> ${failed[*]:-}" 
[[ ${#failed[@]} -eq 0 ]] || exit 1
