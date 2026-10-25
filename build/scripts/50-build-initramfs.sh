#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ART="$REPO_ROOT/artifacts"
IMG="$ART/initramfs-aether.img"
STAGE="$ART/initramfs-stage"; rm -rf "$STAGE"; mkdir -p "$STAGE"/{bin,dev,proc,sys,run,newroot,hooks,usr/bin}
# busybox (static) required
if command -v busybox >/dev/null 2>&1 && file "$(command -v busybox)" | grep -q static; then
  cp "$(command -v busybox)" "$STAGE/bin/busybox"
else
  echo "[50] static busybox not found; trying mkinitcpio path" >&2
  if command -v mkinitcpio >/dev/null 2>&1 && [[ -f "$ART/rootfs/boot/vmlinuz-aether" || -f "$ART/kernel/vmlinuz-aether" ]]; then
    mkdir -p "$ART/rootfs/boot"
    cp "$ART/kernel/vmlinuz-aether" "$ART/rootfs/boot/" 2>/dev/null || true
    mkinitcpio -c /dev/null -g "$IMG" 2>/dev/null || true
  fi
fi
for app in sh mount umount ls mkdir mknod switch_root modprobe cryptsetup sleep cat sed awk grep sha256sum; do
  if [[ -x "$STAGE/bin/busybox" ]]; then
    ln -sf /bin/busybox "$STAGE/usr/bin/$app" 2>/dev/null || true
  fi
done
for conf in storage-discovery.conf cryptsetup.conf root-mount.conf switch-root.conf modules-load.conf; do
  cp "$REPO_ROOT/boot/initramfs/$conf" "$STAGE/"
done
cp "$REPO_ROOT/boot/initramfs/init" "$STAGE/init"; chmod 755 "$STAGE/init"
for h in "$REPO_ROOT"/boot/initramfs/hooks/*; do cp "$h" "$STAGE/hooks/"; chmod 755 "$STAGE/hooks/$(basename "$h")"; done
if command -v cryptsetup >/dev/null 2>&1; then cp "$(command -v cryptsetup)" "$STAGE/usr/bin/"; fi
if [[ -x "$STAGE/bin/busybox" ]]; then
  (cd "$STAGE" && find . | cpio -o -H newc --owner root:root | zstd -19 -o "$IMG")
  echo "[50] initramfs built: $IMG"
else
  [[ -f "$IMG" ]] || { echo "[50] ERROR: no initramfs produced" >&2; exit 1; }
fi
