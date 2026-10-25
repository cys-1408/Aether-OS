"""Truthful response composition (mode-labeled, step-by-step)."""
from __future__ import annotations


def compose(task: dict, results: list[dict]) -> str:
    mode = task.get("plan", {}).get("mode", "rule-based")
    lines = []
    ok = [r for r in results if r.get("outcome") == "ok" and r.get("verified", False)]
    failed = [r for r in results if r.get("outcome") != "ok"]
    for r in ok:
        detail = _describe(r)
        lines.append(f"Done: {detail}")
    for r in failed:
        lines.append(f"Failed: {r.get('capability_id')} — {r.get('error', 'unknown reason')}")
    if not results:
        lines.append(task.get("plan", {}).get("note", "Nothing to do."))
    lines.append(f"({mode} mode · {len(ok)} verified, {len(failed)} not completed)")
    return "\n".join(lines)


def _describe(result: dict) -> str:
    cap = result.get("capability_id")
    data = result.get("result") or {}
    if cap == "search_files":
        hits = data.get("results", [])
        return f"found {len(hits)} file(s)" + (f", e.g. {hits[0].get('filename')}" if hits else "")
    if cap in ("open_app",):
        return f"opened {data.get('launched', data.get('app', 'app'))}"
    if cap in ("start_focus_session", "start_break"):
        return f"focus session started ({data.get('minutes', '?')} min)"
    if cap == "tile_windows":
        return f"tiled {data.get('tiled', '?')} windows"
    if cap == "get_cpu_memory_status":
        return f"system: {data}"
    return f"{cap} completed"
