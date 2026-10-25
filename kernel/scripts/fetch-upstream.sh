#!/usr/bin/env bash
# Fetch the pinned upstream kernel source and record its digest.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCK="$REPO_ROOT/kernel/upstream.lock"
ART="$REPO_ROOT/artifacts/kernel-source"
mkdir -p "$ART"

get() { grep -E "^$1 = " "$LOCK" | head -n1 | sed "s/^$1 = //"; }
VER="$(get version)"; URL="$(get url)"; TAG="$(get tag)"
TARBALL="$ART/linux-$VER.tar.xz"

echo "[fetch-upstream] version=$VER url=$URL"
if [[ ! -f "$TARBALL" ]]; then
  curl -fL --retry 3 -o "$TARBALL" "$URL"
fi
SHA="$(sha256sum "$TARBALL" | awk '{print $1}')"
echo "[fetch-upstream] sha256=$SHA"
# Record the digest in the lock (idempotent).
sed -i "s|^sha256 = .*|sha256 = $SHA|" "$LOCK"
echo "[fetch-upstream] OK"
