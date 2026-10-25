#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
echo "[00] verifying toolchain"
"$REPO_ROOT/toolchain/scripts/verify-toolchain.sh"
need_gb=30
avail_gb=$(df --output=avail -BG "$REPO_ROOT" | tail -1 | tr -dc '0-9')
if (( avail_gb < need_gb )); then
  echo "[00] ERROR: only ${avail_gb}GB free; ${need_gb}GB required" >&2; exit 1
fi
echo "[00] host OK (${avail_gb}GB free)"
