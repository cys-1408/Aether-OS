"""fstab + crypttab generation from real device UUIDs/labels."""
from __future__ import annotations

import subprocess
from pathlib import Path


def _probe_uuid(device: str) -> str:
    out = subprocess.run(["blkid", "-s", "UUID", "-o", "value", device],
                         capture_output=True, text=True, timeout=30)
    uuid = out.stdout.strip()
    if not uuid:
        out = subprocess.run(["cryptsetup", "luksUUID", device],
                             capture_output=True, text=True, timeout=30)
        uuid = out.stdout.strip()
    return uuid


def build_fstab(*, root_device: str, esp_device: str | None,
                encrypted: bool, dry_run: bool = False) -> dict:
    """fstab for the mounted target. Root device may be a mapper path."""
    uuid = "" if dry_run else _probe_uuid(root_device)
    lines: list[str] = []
    source = _probe_uuid(root_device) if not encrypted and uuid else None
    if encrypted:
        # mounted mapper: identify the underlying LUKS partition
        lines.append(f"/dev/mapper/aether-root  /  ext4  rw,relatime  0 1")
    elif uuid:
        lines.append(f"UUID={uuid}  /  ext4  rw,relatime  0 1")
    else:
        lines.append(f"{root_device}  /  ext4  rw,relatime  0 1")
    if esp_device:
        esp_uuid = "" if dry_run else _probe_uuid(esp_device)
        if esp_uuid:
            lines.append(f"UUID={esp_uuid}  /efi  vfat  rw,umask=0077  0 2")
        else:
            lines.append(f"{esp_device}  /efi  vfat  rw,umask=0077  0 2")
    lines.append("tmpfs  /tmp  tmpfs  rw,nosuid,nodev,size=2G,mode=1777  0 0")
    root_uuid = uuid if (uuid and not encrypted) else ("" if encrypted else uuid)
    return {"fstab": "\n".join(lines) + "\n",
            "root_uuid": (_probe_uuid(root_device) if not dry_run and encrypted else root_uuid)}


def build_crypttab(luks_uuid: str | None) -> str | None:
    if not luks_uuid:
        return None
    return ("# <name>  <UUID>  <keyfile>  <options>\n"
            "aether-root  UUID=" + luks_uuid + "  none  luks,discard\n")


def write_target_files(fstab: str, crypttab: str | None = None) -> dict:
    """Write fstab (+crypttab) into the *mounted* target root at /mnt/etc."""
    etc = Path("/mnt/etc")
    etc.mkdir(parents=True, exist_ok=True)
    (etc / "fstab").write_text(fstab)
    if crypttab:
        (etc / "crypttab").write_text(crypttab)
    return {"fstab": "/mnt/etc/fstab", "crypttab": crypttab and "/mnt/etc/crypttab"}


# Back-compat flat writer kept for older callers.
def write_fstab(root_mnt: str, encrypted: bool) -> str:
    data = build_fstab(root_device=root_mnt, esp_device=None,
                       encrypted=encrypted, dry_run=False)
    (Path(root_mnt) / "etc").mkdir(parents=True, exist_ok=True)
    (Path(root_mnt) / "etc/fstab").write_text(data["fstab"])
    if encrypted:
        (Path(root_mnt) / "etc/crypttab").write_text(build_crypttab(
            _probe_uuid("/dev/mapper/aether-root")))
    return data["fstab"]
