"""Generate concepts via Runtime; HONEST pending when model unavailable."""
from __future__ import annotations

import json

from concept_prompt import concept_prompt


def generate_concepts(runtime_socket: str, record: dict, config: dict) -> dict:
    """Returns index_status/concepts/failure_reason fields for the record."""
    attempts = int(config.get("indexing", {}).get("concept_attempts", 3))
    text = record.get("extracted_text") or ""
    if not text and not record.get("filename"):
        return {"index_status": "failed", "concepts": None, "failure_reason": "no content to label"}
    from aether_core.ipc import call
    from aether_core.errors import IpcError
    last_error = None
    for attempt in range(max(1, attempts)):
        try:
            result = call(runtime_socket, "Runtime.infer", {
                "request_id": f"concept-{record['file_id']}-{attempt}",
                "task_class": "concept",
                "prompt": concept_prompt(text or record["filename"]),
                "max_tokens": 64, "temperature": 0.1, "timeout_s": 30}, timeout=40)
            raw = (result or {}).get("text") or ""
            parsed = _parse_concepts(raw)
            if parsed is not None:
                return {"index_status": "ready", "concepts": parsed, "failure_reason": None}
            last_error = "malformed model output"
        except IpcError as e:
            last_error = f"runtime unavailable: {e.message}"
            break
        except Exception as e:  # noqa: BLE001
            last_error = str(e)
    return {"index_status": "failed", "concepts": None, "failure_reason": last_error}


def _parse_concepts(raw: str) -> list[str] | None:
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data = json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return None
    concepts = data.get("concepts")
    if not isinstance(concepts, list):
        return None
    normalized = concept_normalizer.normalize(concepts)
    if concept_validator.valid(normalized):
        return normalized
    return None
