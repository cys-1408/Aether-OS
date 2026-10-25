#!/usr/bin/env bash
# Assemble the real filesystem hierarchy from packages + configuration.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ART="$REPO_ROOT/artifacts"; RFS="$ART/rootfs"
mkdir -p "$RFS"
echo "[40] assembling rootfs at $RFS"
# Directory layout (permissions manifest governs modes)
python3 - "$REPO_ROOT" "$RFS" <<'EOF'
import sys, pathlib, yaml, os
repo, rfs = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
layout = yaml.safe_load((repo/"build/rootfs/directory-layout.yaml").read_text())
for d in layout.get("directories", []):
    (rfs / d["path"]).mkdir(parents=True, exist_ok=True)
    mode = d.get("mode")
    if mode: os.chmod(rfs / d["path"], int(mode, 8))
EOF
# Base userland: pacstrap when available (Arch host), else document requirement
if command -v pacstrap >/dev/null 2>&1; then
  pacstrap -c -G -M "$RFS" base linux-aether systemd pacman networkmanager \
    pipewire wireplumber sway gtk3 python python-yaml python-gobject grub \
    mkinitcpio cryptsetup e2fsprogs dosfstools polkit dbus linux-firmware \
    noto-fonts $( [[ -d "$REPO_ROOT/artifacts/repo" ]] && echo --needed ) || \
  { echo "[40] pacstrap failed — repo/packages incomplete?" >&2; exit 1; }
else
  echo "[40] pacstrap unavailable on this host; stage Aether payload + configs only."
fi
# Aether payload: copy tree into FHS locations
mkdir -p "$RFS/usr/libexec/aether" "$RFS/usr/lib/aether/python" "$RFS/usr/share/aether" "$RFS/etc"
cp -r "$REPO_ROOT/libraries/libaether-core/python/aether_core" "$RFS/usr/lib/aether/python/"
for svc in services/*/*/ services/notifications services/clipboard services/printing services/logging services/backup; do
  [[ -d "$svc" && -f "$svc/main.py" ]] || continue
  name=$(basename "$svc"); cp -r "$svc" "$RFS/usr/libexec/aether/$name" 2>/dev/null || true
done
for top in ai intentfs miso desktop installer recovery package-manager updater; do
  cp -r "$REPO_ROOT/$top" "$RFS/usr/libexec/aether/$top"
done
cp -r "$REPO_ROOT/system" "$RFS/usr/lib/systemd-aether-src"
cp -r "$REPO_ROOT/system/services" "$RFS/etc/systemd/system/" 2>/dev/null || true
cp -r "$REPO_ROOT/system/targets" "$RFS/etc/systemd/system/" 2>/dev/null || true
cp -r "$REPO_ROOT/system/timers" "$RFS/etc/systemd/system/" 2>/dev/null || true
cp -a "$REPO_ROOT/rootfs/etc/aether" "$RFS/etc/"
cp -a "$REPO_ROOT/rootfs/etc/os-release" "$REPO_ROOT/rootfs/etc/hostname" "$REPO_ROOT/rootfs/etc/issue" "$RFS/etc/" 2>/dev/null || true
cp -a "$REPO_ROOT/rootfs/etc/sysusers.d" "$RFS/etc/" 2>/dev/null || true
cp -a "$REPO_ROOT/rootfs/etc/skel" "$RFS/etc/" 2>/dev/null || true
# Permissions manifest
python3 - "$REPO_ROOT" "$RFS" <<'EOF'
import sys, pathlib, yaml, os
repo, rfs = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
pm = yaml.safe_load((repo/"build/rootfs/permissions-manifest.yaml").read_text())
for e in pm.get("paths", []):
    p = rfs / e["path"]
    if p.exists() and e.get("mode"): os.chmod(p, int(e["mode"], 8))
    if p.exists() and e.get("owner"): print(f"[40] note: chown {e['owner']} {e['path']} applied at image time")
EOF
echo "[40] rootfs assembled"
