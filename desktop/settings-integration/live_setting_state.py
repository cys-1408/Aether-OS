"""Live state snapshots for Settings pages (services consulted for truth)."""
from __future__ import annotations


def service_states() -> dict:
    from aether_core.ipc import call
    from aether_core.errors import IpcError
    from aether_core import paths
    out = {}
    for svc, method in (("audio", "Audio.mic_state"), ("network", "Network.status"),
                        ("runtime", "Runtime.status"), ("intentfs", "IntentFS.status")):
        try:
            out[svc] = call(paths.resolve_socket(svc), method, {}, timeout=4)
        except IpcError as e:
            out[svc] = {"reachable": False, "reason": e.message}
    return out
