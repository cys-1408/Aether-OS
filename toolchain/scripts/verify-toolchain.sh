#!/usr/bin/env bash
set -euo pipefail
LOCK="$(cd "$(dirname "$0")/.." && pwd)/versions.lock"
fail=0
while read -r line; do
  [[ -z "$line" || "$line" == \#* ]] && continue
  tool="${line%% *}"; need="${line##* }"
  case "$tool" in
    python) bin=python3 ;;
    yaml) bin=python3 ;;
    *) bin="$tool" ;;
  esac
  if ! command -v "$bin" >/dev/null 2>&1; then echo "MISSING tool: $tool"; fail=1; continue; fi
  ver=$("$bin" --version 2>/dev/null | head -1)
  echo "ok  $tool  ($ver)"
done < "$LOCK"
python3 -c "import yaml" 2>/dev/null || { echo "MISSING PyYAML"; fail=1; }
exit $fail
