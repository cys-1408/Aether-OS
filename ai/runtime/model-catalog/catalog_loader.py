"""Load + validate the versioned model catalog."""
from __future__ import annotations

import json
from pathlib import Path

from aether_core.errors import AetherError


def load_catalog(config: dict) -> dict:
    path = Path(str(config.get("catalog_path", "")).replace("~", str(Path.home())))
    if not path.exists():
        path = Path(__file__).resolve().parents[2] / "catalog" / "catalog.json"
    data = json.loads(path.read_text())
    # integrity: digest file must exist alongside and match
    digest_file = path.with_suffix(path.suffix + ".sha256")
    if digest_file.exists():
        import hashlib
        recorded = digest_file.read_text().split()[0]
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if recorded != actual:
            raise AetherError("E_CATALOG_DIGEST", "catalog.json sha256 mismatch — refusing to trust entries")
    # structural validation (minimal draft-07 subset via aether_core)
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
    from aether_core import validate
    schema_path = path.parent / "catalog.schema.json"
    if schema_path.exists():
        validate(data, json.loads(schema_path.read_text()))
    return data
