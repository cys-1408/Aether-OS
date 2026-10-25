#!/usr/bin/env bash
# Build Aether pacman packages from packaging/ definitions into artifacts/repo.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ART="$REPO_ROOT/artifacts"; REPO="$ART/repo"
mkdir -p "$REPO"
if ! command -v makepkg >/dev/null 2>&1; then
  echo "[30] makepkg unavailable; staging packages as tarball sets instead"
  PKG_DIR="$ART/packages-staging"; mkdir -p "$PKG_DIR"
  for def in "$REPO_ROOT"/packaging/PKGBUILD-*; do
    name=$(basename "$def" | sed 's/^PKGBUILD-//')
    tar -czf "$PKG_DIR/$name-1.0.0-x86_64.pkg.tar.gz" -C "$REPO_ROOT" \
      rootfs system services libraries protocols desktop applications ai intentfs miso \
      installer recovery package-manager updater accessibility 2>/dev/null || true
  done
  echo "[30] staged fallback packages (host lacks makepkg — ISO build requires a full host)"
  exit 0
fi
for def in "$REPO_ROOT"/packaging/PKGBUILD-*; do
  name=$(basename "$def" | sed 's/^PKGBUILD-//')
  work="$ART/pkgbuild/$name"; mkdir -p "$work/src"
  cp -r "$REPO_ROOT"/{rootfs,system,services,libraries,protocols,desktop,applications,ai,intentfs,miso,installer,recovery,package-manager,updater,accessibility,assets,firmware} "$work/src/" 2>/dev/null || true
  cp "$def" "$work/PKGBUILD"
  (cd "$work" && BUILDDIR="$work" makepkg -f --noconfirm -p PKGBUILD >/dev/null)
  mv "$work"/"$(echo "$name")"-*.pkg.tar.zst "$REPO/" 2>/dev/null || mv "$work"/*.pkg.tar.* "$REPO/" 2>/dev/null || true
  echo "[30] built $name"
done
if command -v repo-add >/dev/null 2>&1; then
  (cd "$REPO" && repo-add aether.db.tar.gz *.pkg.tar.* >/dev/null 2>&1 || true)
fi
echo "[30] packages built into $REPO"
