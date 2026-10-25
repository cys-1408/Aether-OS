#!/usr/bin/env bash
# Produce the actual hybrid bootable ISO (UEFI + BIOS).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ART="$REPO_ROOT/artifacts"
STAGE="$ART/iso-stage"; OUT="$ART/release"
mkdir -p "$OUT"
command -v xorriso >/dev/null 2>&1 || { echo "[90] xorriso required" >&2; exit 1; }
[[ -f "$STAGE/boot/vmlinuz-aether" ]] || { echo "[90] kernel missing from iso-stage" >&2; exit 1; }
[[ -f "$STAGE/boot/initramfs-aether.img" ]] || { echo "[90] initramfs missing" >&2; exit 1; }
[[ -f "$STAGE/boot/grub/grub.cfg" ]] || { echo "[90] grub.cfg missing" >&2; exit 1; }
VOLID="AETHEROS"
EFIBIN=""
[[ -f "$ART/efi-staging/BOOTX64.EFI" ]] && EFIBIN="$ART/efi-staging/BOOTX64.EFI"
EFI_ARGS=()
if [[ -n "$EFIBIN" ]]; then
  mkdir -p "$STAGE/efi/boot"
  cp "$EFIBIN" "$STAGE/efi/boot/BOOTX64.EFI"
  EFI_ARGS=(-e /efi -no-emul-boot)
fi
xorriso -as mkisofs \
  -iso-level 3 -full-iso9660-filenames -volid "$VOLID" \
  -isohybrid-mbr /usr/lib/syslinux/bios/isohdpfx.bin 2>/dev/null || true \
  -b boot/grub/core.img -c boot/grub/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table \
  "${EFI_ARGS[@]}" \
  -isohybrid-gpt-basdat \
  -output "$OUT/aether-os-1.0.0-x86_64.iso" \
  "$STAGE"
ls -la "$OUT"
echo "[90] ISO produced: $OUT/aether-os-1.0.0-x86_64.iso"
echo "[90] NOTE: a release is NOT declared bootable until the acceptance gate in docs/user/installation-guide.md passes on hardware/VM."
