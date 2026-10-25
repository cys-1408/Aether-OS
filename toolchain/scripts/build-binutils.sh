#!/usr/bin/env bash
# On the recommended Arch build host binutils comes from the distro; this
# wrapper documents + verifies instead of vendoring toolchain builds.
set -euo pipefail
command -v ld >/dev/null || { echo "binutils missing" >&2; exit 1; }
ld --version | head -1
echo "[build-binutils] using distro binutils (vendored builds intentionally avoided)"
