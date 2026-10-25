"""Socket path helpers.

Re-exports the canonical ``aether_core.paths`` helpers and adds cross-uid
variants needed by system services that act on behalf of a specific user
(broker, workspace service): ``aether_core.paths.user_socket`` resolves against
the *current* process uid, which is wrong for those callers.
"""

from pathlib import Path

from aether_core.paths import (  # noqa: F401  (re-exported for convenience)
    SYSTEM_CONFIG_DIR,
    SYSTEM_STATE_DIR,
    USER_CONFIG_DIR,
    USER_STATE_DIR,
    system_socket,
    user_socket,
)


def user_socket_for(uid: int, name: str) -> Path:
    """User-session socket path for an arbitrary uid, e.g. the Shell socket."""
    return Path(f"/run/user/{int(uid)}/aether/{name}.sock")


def sway_socket_for(uid: int) -> Path:
    """sway IPC socket path for an arbitrary uid (standard sway location)."""
    return Path(f"/run/user/{int(uid)}/sway-ipc.{int(uid)}.sock")
