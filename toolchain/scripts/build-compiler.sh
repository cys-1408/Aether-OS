#!/usr/bin/env bash
set -euo pipefail
command -v gcc >/dev/null || { echo "gcc missing" >&2; exit 1; }
gcc --version | head -1
echo "[build-compiler] using distro gcc (vendored builds intentionally avoided)"
