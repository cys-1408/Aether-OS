"""Optional AI page: real Runtime recommendation + consent-gated download, or skip."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
from aether_core.ipc import call  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402

RUNTIME_SOCK = "/run/aether/runtime.sock"


def runtime_available() -> bool:
    try:
        call(RUNTIME_SOCK, "Runtime.status", {}, timeout=5)
        return True
    except IpcError:
        return False


def recommendation(task_class: str = "assistant") -> dict:
    try:
        return call(RUNTIME_SOCK, "Runtime.models_recommend", {"task_class": task_class}, timeout=30)
    except IpcError as e:
        return {"available": False, "reason": str(e)}


def download(model_id: str, consent: bool) -> dict:
    if not consent:
        return {"started": False, "reason": "no consent given"}
    try:
        return call(RUNTIME_SOCK, "Runtime.download_start", {"model_id": model_id, "consent": True}, timeout=30)
    except IpcError as e:
        return {"started": False, "reason": str(e)}


def run_cli_prompt() -> dict:
    if not runtime_available():
        print("AI runtime is not running (this is fine — Aether works fully without AI).")
        return {"ai_setup": "skipped"}
    rec = recommendation()
    print("Recommended models:", rec if not rec.get("available", True) else [m.get("name") for m in rec.get("recommendations", [])])
    choice = input("Set up a local AI model now? [y/N]: ").strip().lower() == "y"
    if not choice:
        return {"ai_setup": "skipped"}
    model_id = input("Model id from the list: ").strip()
    result = download(model_id, True)
    print("download started" if result.get("started") else f"not started: {result.get('reason')}")
    return {"ai_setup": "started" if result.get("started") else "failed", "model_id": model_id}


def gtk_widget(commit):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    info = Gtk.Label(label=("Optional: set up a local AI model (downloads over the network, "
                            "after your explicit consent).\nAether works fully without it — you can "
                            "add one later in Settings → AI Runtime."))
    info.set_line_wrap(True)
    rec_label = Gtk.Label(label=str(recommendation()))
    rec_label.set_line_wrap(True)
    setup = Gtk.CheckButton(label="Set up a local AI model now")
    btn = Gtk.Button(label="Continue")

    def _next(_):
        choices = {"ai_setup": "requested" if setup.get_active() else "skipped"}
        if setup.get_active():
            recs = recommendation().get("recommendations", [])
            if recs:
                result = download(recs[0]["model_id"], True)
                choices["model_id"] = recs[0]["model_id"]
                choices["download_started"] = result.get("started", False)
        commit("optional_ai", choices)
    btn.connect("clicked", _next)
    for wd in (info, rec_label, setup, btn):
        box.pack_start(wd, False, False, 0)
    return box
