"""Path scope: allowed roots only; sensitive paths always denied."""
from __future__ import annotations

from pathlib import Path

from aether_core import filesops
from aether_core.config import load_yaml
from aether_core.errors import IpcError

PATH_KEYS = ("path", "src", "dst")


def check_scope(cap: dict, params: dict) -> None:
    provider = cap.get("provider", "")
    if provider not in ("agent-local",):
        return  # desktop/system providers validate their own targets
    policy = load_yaml("/etc/aether/capability-policy.yaml")
    roots = [str(Path(r).expanduser()) for r in policy.get("path_scope", {}).get("allowed_roots", [])]
    denied = [str(Path(d).expanduser()) for d in policy.get("path_scope", {}).get("denied_paths", [])]
    for key in PATH_KEYS:
        if key not in params:
            continue
        target = Path(str(params[key])).expanduser().resolve()
        for d in denied:
            if filesops.is_within(target, Path(d)):
                raise IpcError("E_SCOPE", f"path is in a denied location: {d}")
        if roots and not any(filesops.is_within(target, Path(r)) for r in roots):
            raise IpcError("E_SCOPE", f"path outside allowed roots: {target}")
