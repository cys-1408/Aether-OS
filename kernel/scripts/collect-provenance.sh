#!/usr/bin/env bash
# Record source revision, patch digests, config hash and toolchain versions.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
P="$REPO_ROOT/kernel/provenance"; SRC="$REPO_ROOT/kernel/source/linux"; ART="$REPO_ROOT/artifacts/kernel"
mkdir -p "$P"
get() { grep -E "^$1 = " "$REPO_ROOT/kernel/upstream.lock" | head -n1 | sed "s/^$1 = //"; }
echo "$(get version) $(get tag)" > "$P/upstream-commit.txt"
{ echo "["; first=1
  while IFS= read -r l; do
    case "$l" in ''|'#'*) continue;; esac
    d=$(sha256sum "$REPO_ROOT/kernel/patches/$l" | awk '{print $1}')
    $first || echo ","; first=0
    printf '{"patch": "%s", "sha256": "%s"}' "$l" "$d"
  done < "$REPO_ROOT/kernel/patches/series"
  echo "]"; } > "$P/patch-manifest.json"
sha256sum "$ART/aether-merged.config" | awk '{print $1}' > "$P/config-hash.txt"
{
  echo '{"gcc": "'$(gcc --version | head -1 | awk '{print $3}')'", "binutils": "'$(ld --version | head -1 | awk '{print $NF}')'", "make": "'$(make --version | head -1 | awk '{print $3}')'", "flex": "'$(flex --version 2>/dev/null | awk '{print $2}' || echo absent)'", "bison": "'$(bison --version 2>/dev/null | awk '{print $NF}' || echo absent)'"}'
} > "$P/toolchain-manifest.json"
echo "[collect-provenance] written to $P"
