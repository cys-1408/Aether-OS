#!/usr/bin/env bash
# Verify the pinned source identity and integrity BEFORE building.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCK="$REPO_ROOT/kernel/upstream.lock"
get() { grep -E "^$1 = " "$LOCK" | head -n1 | sed "s/^$1 = //"; }
SHA="$(get sha256)"; TARBALL="$REPO_ROOT/artifacts/kernel-source/linux-$(get version).tar.xz"
if [[ "$SHA" == UNFILLED-RECORD-AT-FETCH ]]; then
  echo "ERROR: upstream.lock sha256 is unfilled. Run scripts/fetch-upstream.sh first." >&2
  exit 1
fi
[[ -f "$TARBALL" ]] || { echo "ERROR: $TARBALL missing" >&2; exit 1; }
ACTUAL="$(sha256sum "$TARBALL" | awk '{print $1}')"
if [[ "$ACTUAL" != "$SHA" ]]; then
  echo "ERROR: kernel source digest mismatch: recorded=$SHA actual=$ACTUAL" >&2
  exit 1
fi
echo "[verify-upstream] source integrity OK ($SHA)"
