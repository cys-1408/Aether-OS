#!/usr/bin/env bash
# Apply the declared patch series to the extracted tree; fail on any mismatch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$REPO_ROOT/kernel/source/linux"
PATCHES="$REPO_ROOT/kernel/patches"
cd "$SRC"
while IFS= read -r p; do
  case "$p" in ''|'#'*) continue;; esac
  echo "[apply-patches] $p"
  patch -p1 --forward < "$PATCHES/$p"
done < "$PATCHES/series"
echo "[apply-patches] series applied (empty series = no-op)"
