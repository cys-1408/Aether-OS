#!/usr/bin/env bash
# Build the actual upstream kernel for x86-64 (bzImage + modules + headers).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
"$REPO_ROOT/kernel/scripts/verify-upstream.sh"
SRC="$REPO_ROOT/kernel/source/linux"
ART="$REPO_ROOT/artifacts/kernel"
mkdir -p "$ART"
[[ -d "$SRC" ]] || { echo "extract source first (fetch-upstream)" >&2; exit 1; }
"$REPO_ROOT/kernel/scripts/apply-patches.sh"
"$REPO_ROOT/kernel/scripts/merge-config.sh"
CONFIG="$REPO_ROOT/artifacts/kernel/aether-merged.config"
cp "$CONFIG" "$SRC/.config"
make -C "$SRC" ARCH=x86_64 -j"$(nproc)" bzImage modules
make -C "$SRC" ARCH=x86_64 modules_install INSTALL_MOD_PATH="$ART/modules"
cp "$SRC/arch/x86/boot/bzImage" "$ART/vmlinuz-aether"
cp "$SRC/System.map" "$ART/System.map"
echo "[build-kernel] done: $ART/vmlinuz-aether"
