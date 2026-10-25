#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ART="$REPO_ROOT/artifacts"
BOOT="$ART/iso-stage/boot/grub"; mkdir -p "$BOOT"
# Render grub.cfg with cmdline profiles
NORM=$(tr '\n' ' ' < "$REPO_ROOT/boot/kernel-cmdline/normal.conf")
INST=$(tr '\n' ' ' < "$REPO_ROOT/boot/kernel-cmdline/installer.conf")
RECO=$(tr '\n' ' ' < "$REPO_ROOT/boot/kernel-cmdline/recovery.conf")
sed -e "s|@NORMAL_CMDLINE@|$NORM|" -e "s|@RECOVERY_CMDLINE@|$RECO|" \
    "$REPO_ROOT/boot/grub/grub.cfg.in" > "$BOOT/grub.cfg"
# Live media uses installer entry as default first entry
cat >> "$BOOT/grub.cfg" <<EOF2
menuentry "Install Aether OS" --class aether --class os {
    linux /boot/vmlinuz-aether $INST
    initrd /boot/initramfs-aether.img
}
EOF2
# Background image from wallpaper (if rsvg-convert available)
if command -v rsvg-convert >/dev/null 2>&1; then
  rsvg-convert -w 1920 -h 1080 "$REPO_ROOT/desktop/assets/wallpapers/aether-warm.svg" -o "$BOOT/background.png" || true
fi
# EFI + BIOS boot images (if grub tools available)
mkdir -p "$ART/efi-staging"
if command -v grub-mkstandalone >/dev/null 2>&1; then
  grub-mkstandalone -O x86_64-efi -o "$ART/efi-staging/BOOTX64.EFI" \
    "boot/grub/grub.cfg=boot/grub/grub.cfg" 2>/dev/null || \
    grub-mkstandalone -O x86_64-efi -o "$ART/efi-staging/BOOTX64.EFI" "$BOOT/grub.cfg" || true
fi
if command -v grub-mkimage >/dev/null 2>&1; then
  grub-mkimage -O i386-pc -o "$ART/iso-stage/boot/grub/core.img" biosdisk part_msdos part_gpt iso9660 2>/dev/null || true
fi
mkdir -p "$ART/iso-stage/boot"
cp "$ART/kernel/vmlinuz-aether" "$ART/iso-stage/boot/vmlinuz-aether" 2>/dev/null || \
  cp "$ART/rootfs/boot/vmlinuz-aether" "$ART/iso-stage/boot/vmlinuz-aether"
cp "$ART/initramfs-aether.img" "$ART/iso-stage/boot/initramfs-aether.img"
echo "[60] bootloader staged"
