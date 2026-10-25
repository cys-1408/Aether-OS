"""Identity: agent-kind requests must match the peer uid."""
from __future__ import annotations

from aether_core.errors import IpcError


def check(requester: dict, peer_uid: int) -> None:
    kind = requester.get("kind", "app")
    uid = requester.get("uid", -1)
    if kind in ("agent", "app") and uid != peer_uid:
        raise IpcError("E_IDENTITY", f"requester uid {uid} != peer uid {peer_uid}")
