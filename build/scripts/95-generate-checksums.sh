#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$REPO_ROOT/artifacts/release"
cd "$OUT"
sha256sum aether-os-*.iso > SHA256SUMS
echo "[95] checksums written"; cat SHA256SUMS
