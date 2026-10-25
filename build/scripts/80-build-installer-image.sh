#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ART="$REPO_ROOT/artifacts"
# The installer runs in the live environment; stage packages + repo for offline install
ISO_STAGE="$ART/iso-stage"
mkdir -p "$ISO_STAGE/repo" "$ISO_STAGE/aether"
cp -r "$ART/repo"/* "$ISO_STAGE/repo/" 2>/dev/null || echo "[80] WARN no package repo staged"
cp -r "$REPO_ROOT/installer" "$ISO_STAGE/aether/installer"
cp -r "$REPO_ROOT/system" "$ISO_STAGE/aether/system"
echo "[80] installer environment staged"
