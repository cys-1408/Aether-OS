"""aether-hardware-probe — real hardware facts, unknowns explicit."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # services/common
sys.path.insert(0, Path(__file__).resolve().parents[4].as_posix() + "/libraries/libaether-core/python")

from service_main import SystemService  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402

from cpu_probe import cpu_facts
from memory_probe import memory_facts
from accelerator_probe import accelerators
from storage_probe import storage_facts, smart_health
from network_probe import network_facts
from audio_probe import audio_facts
from display_probe import display_facts
from thermal_probe import thermal_facts
from battery_probe import power_facts
from firmware_probe import firmware_facts


def full_profile() -> dict:
    return {
        "schema_version": "1.0.0",
        "cpu": cpu_facts(),
        "memory": memory_facts(),
        "accelerators": accelerators(),
        "storage": storage_facts(),
        "network": network_facts(),
        "audio": audio_facts(),
        "display": display_facts(),
        "thermal": thermal_facts(),
        "power": power_facts(),
        "firmware": firmware_facts(),
        "unknown_fields": [],
    }


def build_service() -> SystemService:
    return SystemService("hardware-probe", "hardware-probe", {
        "Hardware.cpu": lambda p: cpu_facts(),
        "Hardware.memory": lambda p: memory_facts(),
        "Hardware.accelerators": lambda p: {"accelerators": accelerators()},
        "Hardware.storage": lambda p: {"disks": storage_facts()},
        "Hardware.disk_health": lambda p: smart_health(str(p.get("disk", ""))) if p.get("disk") else (_ for _ in ()).throw(IpcError("E_INVALID", "disk required")),
        "Hardware.network": lambda p: {"interfaces": network_facts()},
        "Hardware.audio": lambda p: audio_facts(),
        "Hardware.display": lambda p: {"connectors": display_facts()},
        "Hardware.thermal": lambda p: {"zones": thermal_facts()},
        "Hardware.power": lambda p: power_facts(),
        "Hardware.firmware": lambda p: firmware_facts(),
        "Hardware.summary": lambda p: {
            "cpu": cpu_facts(), "memory": memory_facts(),
            "accelerators": accelerators(), "power": power_facts(),
        },
        "Hardware.profile": lambda p: full_profile(),
    })


if __name__ == "__main__":
    svc = build_service()
    svc.run()
