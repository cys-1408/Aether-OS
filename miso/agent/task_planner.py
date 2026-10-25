"""Plan builder: rule-based templates + optional model refinement (labeled)."""
from __future__ import annotations

import time

from intent_classifier import classify

TEMPLATES = {
    "find_file": [{"capability_id": "search_files", "params": {"query": "$text"}}],
    "open_app": [{"capability_id": "open_app", "params": {"app": "$app"}}],
    "focus": [{"capability_id": "start_focus_session", "params": {"minutes": 25}}],
    "break": [{"capability_id": "start_break", "params": {"minutes": 5}}],
    "organize": [{"capability_id": "tile_windows", "params": {}}],
    "status": [{"capability_id": "get_cpu_memory_status", "params": {}}],
    "model": [{"capability_id": "recommend_model", "params": {"task_class": "assistant"}}],
    "workspace": [{"capability_id": "save_workspace", "params": {"name": "last-layout"}}],
}


def build_plan(text: str, registry: dict, config: dict) -> dict:
    intent, confidence = classify(text)
    steps_spec = TEMPLATES.get(intent)
    if not steps_spec:
        return {"plan_id": f"p-{int(time.time()*1000)}", "intent": "unknown",
                "mode": "rule-based", "steps": [],
                "needs_confirmation": False,
                "note": "I don't have a safe plan for that yet — try one of the suggestions."}
    steps = []
    needs = False
    for i, spec in enumerate(steps_spec, 1):
        cap = registry.get(spec["capability_id"], {})
        params = dict(spec["params"])
        for k, v in params.items():
            if v == "$text":
                params[k] = text.replace("find a file", "").replace("find file", "").strip() or text
        risk = cap.get("risk_class", "write")
        steps.append({"index": i, "capability_id": spec["capability_id"], "params": params,
                      "risk_class": risk, "confirmation": cap.get("confirmation", "policy"),
                      "undoable": bool((cap.get("undo") or {}).get("supported"))})
        needs = needs or risk in ("write", "destructive") or cap.get("confirmation") == "always"
    return {"plan_id": f"p-{int(time.time()*1000)}", "intent": intent,
            "mode": "rule-based", "steps": steps, "needs_confirmation": needs}
