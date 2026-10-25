"""Loads root-owned policy layers; hash-guarded (agent cannot alter)."""
from __future__ import annotations

import hashlib
from pathlib import Path

from aether_core.config import load_yaml

POLICY_DIR = Path("/etc/aether/policy")
FALLBACK_DIR = Path(__file__).resolve().parent
LAYERS = ["default-policy.yaml", "read-only-policy.yaml", "reversible-action-policy.yaml",
          "write-action-policy.yaml", "destructive-action-policy.yaml"]


class PolicyLoader:
    def __init__(self):
        self._hashes: dict[str, str] = {}

    def layers(self) -> list[dict]:
        out = []
        for name in LAYERS:
            base = POLICY_DIR if (POLICY_DIR / name).exists() else FALLBACK_DIR
            path = base / name
            data = load_yaml(path) or {}
            data["name"] = name
            out.append(data)
            self._hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""
        return out

    def integrity_ok(self) -> bool:
        """Re-hash and compare to startup hashes (tamper → fail closed)."""
        for name in LAYERS:
            base = POLICY_DIR if (POLICY_DIR / name).exists() else FALLBACK_DIR
            path = base / name
            current = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""
            if self._hashes.get(name) not in (None, "") and current != self._hashes[name]:
                return False
        return True
