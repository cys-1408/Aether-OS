"""Error mapping decorator: AetherError -> IpcError with service context."""
from __future__ import annotations

import functools
from aether_core.errors import AetherError, IpcError


def ipc_errors(service: str):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except IpcError:
                raise
            except AetherError as e:
                raise IpcError(e.code, f"{service}: {e.message}", retriable=e.retriable, details=e.details) from e
            except FileNotFoundError as e:
                raise IpcError("E_NOT_FOUND", f"{service}: {e}") from e
            except PermissionError as e:
                raise IpcError("E_DENIED", f"{service}: {e}") from e
        return wrapper
    return deco
