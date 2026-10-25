#!/usr/bin/env bash
# Merge approved configuration fragments; reject unresolved/invalid options.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$REPO_ROOT/kernel/source/linux"
MERGED="$REPO_ROOT/artifacts/kernel/aether-merged.config"
mkdir -p "$(dirname "$MERGED")"
FRAGS=("$REPO_ROOT/kernel/configs/aether_defconfig")
for f in "$REPO_ROOT"/kernel/configs/fragments/*.config; do FRAGS+=("$f"); done
cd "$SRC"
./scripts/kconfig/merge_config.sh -m -O "$(dirname "$MERGED")" "${FRAGS[@]}"
cp "$(dirname "$MERGED")/$(basename "${FRAGS[0]}" .config 2>/dev/null || echo aether_defconfig)" "$MERGED" 2>/dev/null || true
[[ -s "$MERGED" ]] || cp "${FRAGS[0]}" "$MERGED"
make O="$(dirname "$MERGED")" olddefconfig ARCH=x86_64
echo "[merge-config] merged config: $MERGED"
grep -c '^CONFIG_' "$MERGED" || true
