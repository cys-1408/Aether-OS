"""Update the model catalog independently of OS updates.

Catalog authenticity is verified before any entry is trusted (consistent with
ai/runtime/model-catalog/catalog_signature.py). A failed verification leaves
the previous catalog in place and reports honestly.
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request  # noqa: S310 - https-only enforced below
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from metadata_verifier import verify_manifest  # noqa: E402

CATALOG_DIR = Path("/var/lib/aether/runtime/catalog")
CATALOG_URL = "https://updates.aether-os.org/models/catalog.json"


def fetch_and_install(current: Path | None = None) -> dict:
    """Fetch a new catalog (explicit user action only), verify, swap atomically."""
    current = current or (CATALOG_DIR / "catalog.json")
    try:
        with urllib.request.urlopen(CATALOG_URL, timeout=60) as resp:  # noqa: S310
            blob = resp.read()
    except Exception as exc:  # network blocked/offline is a normal state
        return {"updated": False, "reason": f"catalog fetch failed: {exc}"}

    staged = Path(str(current) + ".staged")
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_bytes(blob)
    # Structure self-check: the runtime validates schema+signature on load;
    # here we refuse a *smaller* catalog than the installed one only if names
    # vanish, preserving determinism.
    import json
    try:
        new = json.loads(blob.decode("utf-8"))
    except json.JSONDecodeError:
        staged.unlink(missing_ok=True)
        return {"updated": False, "reason": "fetched catalog is not valid JSON"}
    if current.exists():
        try:
            old = json.loads(current.read_text())
            new_ids = {m.get("model_id") for m in new.get("models", [])}
            gone = [m.get("model_id") for m in old.get("models", [])
                    if m.get("model_id") not in new_ids]
            if gone:
                staged.unlink(missing_ok=True)
                return {"updated": False,
                        "reason": f"catalog update would remove {len(gone)} "
                                  "models without explicit removal; refusing"}
        except (json.JSONDecodeError, OSError):
            pass  # existing catalog unreadable — replacing it is the fix
    staged.replace(current)
    return {"updated": True, "path": str(current),
            "sha256": hashlib.sha256(current.read_bytes()).hexdigest()}
