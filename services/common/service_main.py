"""SystemService base: config, logging, JSON-RPC socket, health, clean shutdown."""
from __future__ import annotations

import json
import os
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "libraries/libaether-core/python"))

from aether_core.ipc import JsonRpcServer, call  # noqa: E402
from aether_core.config import atomic_write_json  # noqa: E402
from aether_core import logging_setup  # noqa: E402


class SystemService:
    """Base class for every aether-* daemon.

    Subclass and pass methods={...}. Health state is published to
    /run/aether/health-<name>.json and every server also answers Health.ping.
    """

    def __init__(self, name: str, socket_name: str, methods: dict[str, Callable[[dict], dict]],
                 *, socket_group: str | None = None, config_file: str | None = None):
        self.name = name
        self.socket_name = socket_name
        self.user_methods = dict(methods)
        self.socket_group = socket_group
        self.config = {}
        self.config_file = config_file or f"/etc/aether/{name}.yaml"
        self.started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        self.last_error: str | None = None
        self.log = logging_setup.configure_logging(name)
        methods = dict(self.user_methods)
        methods.setdefault("Health.ping", lambda p: {"pong": True, "service": name})
        methods.setdefault("X.info", self._info)
        self.methods = methods
        self.server = JsonRpcServer(self.socket_path(), methods, socket_group=socket_group)

    # -- paths -------------------------------------------------------------
    def socket_path(self) -> Path:
        from aether_core import paths
        user_scoped = self.socket_name in ("shell", "agent", "trash", "clipboard", "reminders")
        return paths.user_socket(self.socket_name) if user_scoped else paths.system_socket(self.socket_name)

    # -- info/health ---------------------------------------------------------
    def _info(self, params: dict) -> dict:
        from aether_core.version import VERSION, API_VERSIONS
        return {"service": self.name, "version": VERSION, "api_version": API_VERSIONS.get(self.name.split("-")[0], 1)}

    def health_status(self) -> dict:
        return {"name": self.name, "state": "ready", "started_at": self.started_at,
                "last_error": self.last_error, "pid": os.getpid(),
                "socket": str(self.socket_path())}

    def publish_health(self, state: str | None = None, error: str | None = None) -> None:
        status = self.health_status()
        if state:
            status["state"] = state
        if error:
            status["last_error"] = error
            self.last_error = error
        try:
            atomic_write_json(Path(f"/run/aether/health-{self.name}.json"), status, mode=0o644)
        except OSError:
            pass

    # -- run -----------------------------------------------------------------
    def run(self) -> None:
        self.config = self.load_config()
        self.log.info(f"starting {self.name} on {self.socket_path()}")
        self.publish_health("ready")
        t = threading.Thread(target=self.server.serve_forever, daemon=True)
        t.start()
        signal.signal(signal.SIGTERM, self._on_term)
        try:
            while not self._stopping.is_set():
                time.sleep(0.5)
        finally:
            self.publish_health("stopped")
            self.log.info(f"{self.name} stopped")

    _stopping = threading.Event()

    def _on_term(self, signum, frame) -> None:
        self._stopping.set()
        self.server.stop()

    def stop(self) -> None:
        self._stopping.set()
        self.server.stop()

    # -- config ----------------------------------------------------------------
    def load_config(self) -> dict:
        from aether_core.config import load_yaml
        cfg = load_yaml(self.config_file)
        if not cfg:
            self.log.info(f"no config at {self.config_file}; using defaults")
        return cfg

    # -- helpers for services that need to reach others -------------------------
    @staticmethod
    def call_service(socket_name: str, method: str, params: dict | None = None, timeout: float = 10.0) -> dict | None:
        """Call another Aether service; None (never fabricated data) on failure."""
        from aether_core import paths
        try:
            return call(paths.resolve_socket(socket_name), method, params, timeout=timeout)
        except Exception as e:  # noqa: BLE001 — degrade gracefully
            return None
