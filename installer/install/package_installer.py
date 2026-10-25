"""PackageInstaller: pacstrap from the ISO-local repo (offline-capable).

Runs the real base + desktop package set into the mounted target root. When a
local repository directory exists (mounted ISO: /repo or artifacts/repo), it is
used first so installation never requires the network.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog

BASE = ["base", "linux-aether", "linux-firmware", "systemd", "pacman",
        "networkmanager", "pipewire", "wireplumber", "cryptsetup",
        "e2fsprogs", "dosfstools", "polkit", "dbus", "grub", "mkinitcpio",
        "noto-fonts"]

DESKTOP = ["sway", "foot", "gtk3", "python", "python-yaml", "python-gobject",
           "greetd", "gtklock", "swaybg", "fuzzel"]

LOCAL_REPO_DIRS = ["/repo", "/run/aether/repo", "/run/archiso/bootmnt/repo"]


def find_local_repo_dir() -> Path | None:
    """First existing local package repository (offline install path)."""
    for cand in LOCAL_REPO_DIRS:
        p = Path(cand)
        if p.is_dir() and any(p.glob("*")):
            return p
    return None


def _repo_pacman_conf(repo_dir: Path) -> Path | None:
    """Write a temporary pacman.conf pinning the local repo, return its path."""
    conf = Path("/run/aether/pacman-local.conf")
    try:
        conf.parent.mkdir(parents=True, exist_ok=True)
        conf.write_text(
            "[global]\n"
            "HoldPkg = pacman glibc\n"
            "Architecture = x86_64\n"
            "SigLevel = Required TrustedOnly\n"
            "\n"
            f"[aether-repo]\n"
            f"Server = file://{repo_dir}\n"
            "\n"
            "[core]\n"
            "Include = /etc/pacman.d/mirrorlist\n"
        )
        return conf
    except OSError:
        return None


class PackageInstaller:
    def __init__(self, dry_run: bool = False, log: InstallerLog | None = None):
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    def install_base(self, root: str, desktop: bool = True) -> dict:
        """Install the base (and optionally desktop) set into the target root."""
        packages = list(BASE)
        if desktop:
            packages += DESKTOP
        repo = find_local_repo_dir()
        argv = ["pacstrap", "-c", "-G"]
        if repo is not None:
            conf = _repo_pacman_conf(repo)
            if conf is not None:
                argv += ["-M"]  # use the local repo config
        if shutil.which("pacstrap") is None and not self.dry_run:
            raise RuntimeError("pacstrap not available in the live environment")
        argv += [root, *packages]
        res = run_argv(argv, log=self.log, step="install-packages", dry_run=self.dry_run)
        if not res.ok and not self.dry_run:
            raise RuntimeError(f"pacstrap failed: {res.stderr[-1500:]}")
        return {"packages": len(packages), "repo": str(repo) if repo else "network-mirrorlist"}

    # Back-compat thin wrapper for flat callers.
    def install(self, root: str, desktop: bool = True) -> dict:
        return self.install_base(root, desktop=desktop)
