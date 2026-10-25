"""Partition planner: validated sfdisk script (ESP + root) from a plan dict."""
from __future__ import annotations

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog


def plan_partitions_to_sfdisk_script(plan: dict) -> str:
    """Build the sfdisk script for the chosen plan (validated, printed for
    review the partition_plan_screen)."""
    label = plan.get("label", "gpt")
    esp_size = plan.get("esp_size", "1GiB")
    encrypted = bool(plan.get("encrypted"))
    firmware = plan.get("firmware", "uefi")
    lines = [f"label: {label}"]
    if firmware == "uefi":
        lines.append(f"start=2048, size={esp_size}, type=U, bootable, label=\"AETHER_EFI\"")
    else:
        lines.append(f"start=2048, size=1MiB, type=BIOS boot, bootable")
    lines.append(f"type=Linux filesystem, label=\"AETHEROS\", "
                 f"name=AETHEROS{'-luks' if encrypted else ''}")
    return "\n".join(lines) + "\n"


def validate_script(script: str) -> dict:
    must = ("label:", )
    for m in must:
        if m not in script:
            return {"valid": False, "reason": f"missing {m}"}
    if "label=\"AETHER_EFI\"" not in script and "BIOS boot" not in script:
        return {"valid": False, "reason": "no bootable partition declared"}
    return {"valid": True}


def write_plan(disk: str, dry_run: bool = False, plan: dict | None = None) -> str:
    """Apply the plan to the disk (controller-compat flat entry point)."""
    script = plan_partitions_to_sfdisk_script(plan or {"firmware": "uefi"})
    check = validate_script(script)
    if not check["valid"]:
        raise RuntimeError(f"invalid partition plan: {check['reason']}")
    if dry_run:
        return script
    run_argv(["sfdisk", "--force", disk], input_bytes=script.encode("utf-8"),
             log=InstallerLog(echo=False), step="partition")
    run_argv(["partprobe", disk], log=InstallerLog(echo=False), step="partition")
    return script
