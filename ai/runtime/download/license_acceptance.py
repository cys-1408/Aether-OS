"""License acceptance recording BEFORE download/use."""
from __future__ import annotations

import time

from aether_core import paths
from aether_core.config import atomic_write_json

FILE = paths.SYSTEM_STATE_DIR / "runtime" / "license-acceptances.json"


def record(model_id: str, license_name: str, accepted: bool) -> dict:
    if not accepted:
        from aether_core.errors import IpcError
        raise IpcError("E_LICENSE", "license not accepted — download refused")
    data = {}
    if FILE.exists():
        import json
        data = json.loads(FILE.read_text())
    data[model_id] = {"license": license_name, "accepted_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    atomic_write_json(FILE, data)
    return {"recorded": model_id, "license": license_name}
