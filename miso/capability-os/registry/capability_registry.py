"""Load all capability catalogs into one registry dict."""
from __future__ import annotations

import json
from pathlib import Path

from aether_core import validate

SCHEMA = Path(__file__).resolve().parent / "capability.schema.json"
SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "schemas"


def load_registry() -> dict[str, dict]:
    registry: dict[str, dict] = {}
    meta = json.loads(SCHEMA.read_text())
    for catalog_file in sorted(SCHEMAS_DIR.glob("*.capabilities.json")):
        data = json.loads(catalog_file.read_text())
        validate(data, meta)
        for cap in data.get("capabilities", []):
            cap["_group"] = data.get("group", catalog_file.stem)
            registry[cap["id"]] = cap
    return registry
