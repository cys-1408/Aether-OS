#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ART="$REPO_ROOT/artifacts"
RFS="$ART/rootfs"; LIVE="$ART/live-stage"; mkdir -p "$LIVE"
# Live root = rootfs + live overlay metadata; squashfs of the root
if command -v mksquashfs >/dev/null 2>&1 && [[ -d "$RFS/usr" ]]; then
  mksquashfs "$RFS" "$LIVE/aether-root.squashfs" -comp zstd -noappend >/dev/null
  echo "[70] live squashfs built"
else
  echo "[70] mksquashfs or prepared rootfs missing — live environment incomplete" >&2
  [[ -d "$RFS/usr" ]] || exit 1
fi
cat > "$LIVE/live-metadata.yaml" <<EOF
profile: installer-x86_64
cmdline_file: boot/kernel-cmdline/installer.conf
root_squashfs: aether-root.squashfs
overlay: tmpfs
EOF
echo "[70] live environment assembled"
