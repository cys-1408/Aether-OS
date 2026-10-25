import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2] / 'libraries/libaether-core/python'))
"""Hash-chain integrity verification for the ledger."""
import hashlib


def verify_chain(entries: list[dict]) -> dict:
    prev = None
    for e in entries:
        expected = hashlib.sha256(((prev or "") + e["payload"]).encode()).hexdigest()
        if expected != e.get("entry_hash"):
            return {"chain_ok": False, "broken_at": e.get("entry_id")}
        prev = e.get("entry_hash")
    return {"chain_ok": True, "entries": len(entries)}
