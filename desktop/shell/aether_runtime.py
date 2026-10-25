"""Shared runtime accessors for the Aether shell.

Bridges the shell to :mod:`aether_core` (Agent 3's shared library): JSON-RPC
IPC calls, the sway IPC client, service socket paths and the version string.
All accessors surface TRUE failure reasons instead of inventing data, so
panels can display honest degraded states.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Optional

import shell.pkgmap  # noqa: F401  (registers hyphenated packages + lib path)

LOG = logging.getLogger("aether.shell.runtime")


class AetherCoreUnavailable(RuntimeError):
    """Raised when the shared aether_core package cannot be imported."""


class ServiceCallError(RuntimeError):
    """A user-session/system service call failed (true reason carried)."""

    def __init__(self, code: str, message: str, retriable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retriable = retriable


def _load_aether_core() -> Any:
    """Import aether_core or raise :class:`AetherCoreUnavailable` with the reason."""
    try:
        import aether_core  # noqa: WPS433 - optional at import time by design
        return aether_core
    except Exception as exc:  # ImportError and anything raised by the package
        raise AetherCoreUnavailable(
            f"aether_core library unavailable: {exc.__class__.__name__}: {exc}"
        ) from exc


def aether_core_status() -> tuple[bool, str]:
    """Return ``(available, reason)`` for the shared library import."""
    try:
        _load_aether_core()
        return True, "ok"
    except AetherCoreUnavailable as exc:
        return False, str(exc)


def shell_version() -> str:
    """Version string from aether_core; 'unknown' (honest) when unavailable."""
    try:
        core = _load_aether_core()
        return str(getattr(core.version, "VERSION", "unknown"))
    except AetherCoreUnavailable:
        return "unknown"


# ---------------------------------------------------------------- sockets
def user_socket(name: str) -> Path:
    """User-session socket path: /run/user/$UID/aether/<name>.sock."""
    try:
        core = _load_aether_core()
        return Path(core.paths.user_socket(name))
    except AetherCoreUnavailable:
        uid = os.getuid()
        return Path(f"/run/user/{uid}/aether/{name}.sock")


def system_socket(name: str) -> Path:
    """System service socket path: /run/aether/<name>.sock."""
    try:
        core = _load_aether_core()
        return Path(core.paths.system_socket(name))
    except AetherCoreUnavailable:
        return Path(f"/run/aether/{name}.sock")


SERVICE_SOCKETS: dict[str, str] = {
    "health": "health", "audio": "audio", "network": "network",
    "notifications": "notifications", "ledger": "ledger", "workspace": "workspace",
    "runtime": "runtime", "voice": "voice", "clock": "clock", "storage": "storage",
    "consent": "consent", "logs": "logs",
}


def service_socket(namespace: str) -> Path:
    """Resolve a §4 system service socket for the given namespace."""
    return system_socket(SERVICE_SOCKETS.get(namespace, namespace.lower()))


SHELL_SOCKET = "shell"
AGENT_SOCKET = "agent"


# ---------------------------------------------------------------- IPC calls
def call_service(namespace: str, method: str, params: Optional[dict] = None,
                 *, timeout: float = 10.0) -> dict:
    """Call a system service (namespace like ``Health``/``Audio``/...).

    Raises :class:`ServiceCallError` carrying the true failure reason.
    """
    core = _load_aether_core()
    try:
        result = core.ipc.call(service_socket(namespace),
                               f"{namespace}.{method}", params or {}, timeout=timeout)
        return result if isinstance(result, dict) else {"value": result}
    except Exception as exc:
        retriable = not isinstance(exc, (ValueError, KeyError))
        raise ServiceCallError(
            code=getattr(exc, "code", exc.__class__.__name__),
            message=str(exc),
            retriable=retriable,
        ) from exc


def call_shell(method: str, params: Optional[dict] = None,
               *, timeout: float = 10.0) -> dict:
    """Call the shell's own UDS (used by aetherctl and Miso's broker)."""
    core = _load_aether_core()
    try:
        return core.ipc.call(user_socket(SHELL_SOCKET),
                             f"Shell.{method}", params or {}, timeout=timeout)
    except Exception as exc:
        raise ServiceCallError(
            code=getattr(exc, "code", exc.__class__.__name__),
            message=str(exc),
        ) from exc


def call_agent(method: str, params: Optional[dict] = None,
               *, timeout: float = 60.0) -> dict:
    """Call the Miso agent UDS (Agent.submit / Agent.cancel / Agent.status)."""
    core = _load_aether_core()
    try:
        return core.ipc.call(user_socket(AGENT_SOCKET),
                             f"Agent.{method}", params or {}, timeout=timeout)
    except Exception as exc:
        raise ServiceCallError(
            code=getattr(exc, "code", exc.__class__.__name__),
            message=str(exc),
        ) from exc


# ---------------------------------------------------------------- sway
class CompositorUnavailable(RuntimeError):
    """sway IPC is not reachable (no SWAYSOCK / socket missing / refused)."""


def sway_ipc() -> Any:
    """Return an ``aether_core.swayipc.SwayIPC`` bound to $SWAYSOCK.

    Raises :class:`CompositorUnavailable` with the true reason on failure.
    """
    core = _load_aether_core()
    swaysock = os.environ.get("SWAYSOCK", "")
    if not swaysock:
        raise CompositorUnavailable("SWAYSOCK is not set (not running under sway?)")
    try:
        return core.swayipc.SwayIPC(swaysock)
    except Exception as exc:
        raise CompositorUnavailable(f"sway IPC connect failed: {exc}") from exc


def sway_available() -> tuple[bool, str]:
    """Return ``(available, reason)`` for sway IPC reachability."""
    try:
        ipc = sway_ipc()
        ipc.run_command("nop aether-healthcheck")
        return True, "ok"
    except Exception as exc:
        return False, str(exc)
