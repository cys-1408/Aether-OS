"""Artifact metadata verification from HF API."""
from __future__ import annotations

import json
import urllib.request


def fetch_tree(repo: str) -> list[dict]:
    api = f"https://huggingface.co/api/models/{repo}/tree/main?recursive=true"
    with urllib.request.urlopen(api, timeout=30) as resp:
        return json.loads(resp.read())


def expected_file(repo: str, filename: str) -> dict | None:
    for entry in fetch_tree(repo):
        if entry.get("path") == filename:
            return entry
    return None
