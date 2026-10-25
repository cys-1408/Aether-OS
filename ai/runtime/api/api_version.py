"""API version guard."""
from aether_core.version import API_VERSIONS


def ensure_v1(params: dict) -> None:
    want = int(params.get("api_version", 1))
    if want != API_VERSIONS["runtime"]:
        from aether_core.errors import IpcError
        raise IpcError("E_VERSION", f"runtime api v{API_VERSIONS['runtime']} required, got v{want}")
