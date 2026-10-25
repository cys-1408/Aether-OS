"""Model repair: integrity check + remove broken, re-download via consent."""
from __future__ import annotations


def repair_models(app) -> str:
    models = app.services.call("runtime", "Runtime.models_list", {})
    if not models:
        return "runtime unreachable"
    out = []
    for m in models.get("models", []):
        mid = m.get("model_id")
        result = app.services.call("runtime", "Runtime.warmup", {"model_id": mid}, timeout=120)
        ok = bool(result and result.get("ok"))
        if not ok:
            remove = app.services.call("runtime", "Runtime.model_remove", {"model_id": mid})
            out.append(f"{m.get('name')}: FAILED check → removed ({(remove or {}).get('removed', '?')}); re-download from AI Runtime page")
        else:
            out.append(f"{m.get('name')}: OK")
    return "\n".join(out) or "no installed models"
