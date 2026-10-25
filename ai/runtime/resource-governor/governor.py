"""Governor loop: PSI, battery, thermal, idle unload — every 10s."""
from __future__ import annotations

import threading
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hardware-profile"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "queues"))

from power_thermal_profile import power_state, thermal_state  # noqa: E402
from backpressure import memory_psi_avg10  # noqa: E402


class Governor:
    def __init__(self, service, config: dict):
        self.svc = service
        self.config = config
        self._stop = threading.Event()

    def start(self) -> None:
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self) -> None:
        self._stop.set()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._tick()
            except Exception:
                pass
            self._stop.wait(10)

    def _tick(self) -> None:
        psi = memory_psi_avg10()
        thermal = thermal_state()
        power = power_state()
        actions = []
        if psi is not None and psi > 60:
            actions.append("pause-indexing")
        if psi is not None and psi > 80:
            actions.append("unload-idle-model")
        if thermal == "critical":
            actions.append("pause-inference")
        elif thermal == "hot":
            actions.append("throttle-inference")
        battery = power.get("ac_online")
        if battery is False and self.config.get("battery", {}).get("pause_background_inference", True):
            actions.append("pause-background")
        self.svc.governor_actions = actions
        self.svc._save_state()

    def decisions(self) -> dict:
        return {"actions": getattr(self.svc, "governor_actions", []),
                "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
