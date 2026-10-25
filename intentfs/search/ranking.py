"""Ranking weights (see search_service)."""
from __future__ import annotations

WEIGHTS = {"filename_prefix": 1.0, "filename": 0.9, "path": 0.5,
           "concept": 0.8, "content": 0.6, "freshness": 0.1}
