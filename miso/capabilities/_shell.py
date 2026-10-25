"""Shared helper for desktop-provider capabilities: call the user Shell socket.

The Shell is a user-session service (§4): its socket lives under
/run/user/<uid>/aether/shell.sock. All desktop capabilities funnel through
this helper so error mapping and uid handling stay uniform.
"""

from __future__ import annotations

from aether_core.errors import AetherError
from aether_core.ipc import call as core_call

from miso.socket_paths import user_socket_for

SHELL_TIMEOUT_S = 15.0


def shell_call(uid: int, method: str, params: dict | None, *,
               timeout: float = SHELL_TIMEOUT_S) -> dict:
    """Invoke ``Shell.<method>`` at the requesting user's Shell socket."""
    socket_path = user_socket_for(uid, "shell")
    payload = {k: v for k, v in (params or {}).items() if v is not None}
    try:
        return core_call(socket_path, f"Shell.{method}", payload, timeout=timeout)
    except AetherError as exc:
        code = getattr(exc, "code", "shell_error")
        if code == "ipc_error" or "connect" in exc.message.lower():
            raise AetherError(
                "shell_unavailable",
                f"desktop Shell socket unreachable for uid {uid}: {exc.message}",
                retriable=True, details={"socket": str(socket_path)}) from exc
        raise
