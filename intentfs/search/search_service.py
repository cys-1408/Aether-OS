"""Search service: filename/path (instant) + concepts + text with explainable ranking."""
from __future__ import annotations

import sqlite3


class SearchService:
    def __init__(self, store, config: dict):
        self.store = store
        self.config = config

    def search(self, query: str, filters: dict) -> dict:
        q = (query or "").strip()
        if not q:
            return {"results": [], "query": q}
        low = q.lower()
        scored: dict[str, dict] = {}

        def add(rec, weight, reason):
            path = rec["path"]
            if path not in scored:
                scored[path] = {"record": rec, "score": 0.0, "reasons": []}
            scored[path]["score"] += weight
            scored[path]["reasons"].append(reason)

        with sqlite3.connect(self.store.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM files WHERE tombstoned=0 AND index_status != 'excluded'").fetchall()
        for row in rows:
            rec = self.store._to_record(row)
            name = (rec.get("filename") or "").lower()
            path = (rec.get("path") or "").lower()
            if name.startswith(low):
                add(rec, 1.0, "filename prefix match")
            elif low in name:
                add(rec, 0.9, "filename match")
            elif low in path:
                add(rec, 0.5, "path match")
            for c in rec.get("concepts") or []:
                if low in c or c in low:
                    add(rec, 0.8, f"concept match: {c}")
            if rec.get("index_status") == "ready":
                import time
                age_days = 0.0
                try:
                    import datetime
                    t = datetime.datetime.fromisoformat(rec["indexed_at"][:19])
                    age_days = max(0.0, (datetime.datetime.now() - t).total_seconds() / 86400)
                except Exception:
                    pass
                freshness = 1.0 / (1.0 + age_days / 30.0)
                add(rec, 0.1 * freshness, "freshness boost")
        results = []
        for item in scored.values():
            results.append({
                "filename": item["record"].get("filename"),
                "path": item["record"].get("path"),
                "index_status": item["record"].get("index_status"),
                "concepts": item["record"].get("concepts"),
                "score": round(min(1.0, item["score"]), 3),
                "reasons": item["reasons"],
                "record": item["record"],
            })
        results.sort(key=lambda r: r["score"], reverse=True)
        limit = int(filters.get("limit", self.config.get("search", {}).get("max_results", 50)))
        return {"results": results[:limit], "query": q,
                "note": "scores are relevance, not certainty"}
