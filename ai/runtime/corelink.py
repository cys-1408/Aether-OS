"""Bridge to the shared ``aether_core`` package (CONVENTIONS.md §3).

Every runtime module reaches aether_core through this module so the import
path is wired exactly once and failures surface as clear RuntimeErrors
instead of confusing ImportErrors. Imports are lazy so the package can be
compiled and unit-exercised even while the shared library is being built by
its owning agent; at system-service start-up the presence of aether_core is
mandatory and daemons exit with a truthful message when it is missing.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = REPO_ROOT / "libraries" / "libaether-core" / "python"


def ensure_core_path() -> None:
    """Put the aether_core parent directory on sys.path (idempotent)."""
    if CORE_PATH.is_dir() and str(CORE_PATH) not in sys.path:
        sys.path.insert(0, str(CORE_PATH))


def core_module(name: str) -> Any:
    """Import and return ``aether_core.<name>`` or raise RuntimeError."""
    ensure_core_path()
    try:
        return importlib.import_module(f"aether_core.{name}")
    except Exception as exc:  # ImportError and package-initialisation errors
        raise RuntimeError(f"aether_core.{name} is unavailable: {exc}") from exc


def core_available() -> bool:
    try:
        core_module("version")
        return True
    except RuntimeError:
        return False


# ----------------------------------------------------------------- paths ---
def system_socket(name: str) -> Path:
    return Path(core_module("paths").system_socket(name))


def user_socket(name: str) -> Path:
    return Path(core_module("paths").user_socket(name))


def system_state_dir() -> Path:
    return Path(core_module("paths").SYSTEM_STATE_DIR)


def system_config_dir() -> Path:
    return Path(core_module("paths").SYSTEM_CONFIG_DIR)


# ------------------------------------------------------------------- ipc ---
def ipc_call(socket_path: Path, method: str, params: dict | None = None,
             timeout: float = 10.0) -> dict:
    return core_module("ipc").call(Path(socket_path), method, params, timeout=timeout)


def ipc_error(code: str, message: str, details: Any = None) -> Exception:
    """Build an IpcError compatible with the documented constructor forms."""
    errors = core_module("errors")
    try:
        return errors.IpcError(code=code, message=message, details=details)
    except TypeError:
        err = errors.IpcError(message, -32000)
        err.code = code
        if details is not None:
            err.details = details
        return err


def raise_ipc(code: str, message: str, details: Any = None) -> None:
    raise ipc_error(code, message, details)


# ---------------------------------------------------------------- schema ---
def validate_schema(instance: Any, schema: dict, path: str = "$") -> None:
    core_module("schema").validate(instance, schema, path=path)


# ---------------------------------------------------------------- config ---
def load_yaml(path: Path) -> dict:
    return core_module("config").load_yaml(Path(path))


def atomic_write_text(path: Path, text: str) -> None:
    core_module("config").atomic_write_text(Path(path), text)


def atomic_write_yaml(path: Path, data: dict) -> None:
    core_module("config").atomic_write_yaml(Path(path), data)


def atomic_write_text_safe(path: Path, text: str) -> None:
    """atomic_write_text with a stdlib fallback for early bring-up.

    The fallback performs the same tmp-file + fsync + os.replace sequence;
    behaviour is identical, only the implementation source differs.
    """
    try:
        atomic_write_text(path, text)
        return
    except RuntimeError:
        pass
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        import os as _os
        _os.fsync(handle.fileno())
    import os as _os
    _os.replace(tmp, path)


# ----------------------------------------------------------- cancellation ---
def new_cancellation_token() -> Any:
    return core_module("cancellation").CancellationToken()


# ----------------------------------------------------------------- misc ---
def api_versions() -> dict:
    return dict(core_module("version").API_VERSIONS)


def core_version() -> str:
    return str(core_module("version").VERSION)


def stable_file_id(path: Path) -> str:
    return str(core_module("filesops").stable_file_id(Path(path)))


def configure_logging(service: str, level: str = "INFO") -> None:
    core_module("logging_setup").configure_logging(service, level)
