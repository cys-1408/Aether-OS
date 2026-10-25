"""Aether first-boot wizard (GTK3) — resumable via /var/lib/aether/firstboot-state.json.

Pages: locale -> keyboard -> timezone -> account -> network -> privacy ->
encryption_status -> optional_ai -> completion. Every page commits state as it
finishes so interruption resumes at the right place. The AI page can be skipped
(no-model mode is a first-class outcome). Running as root from tty7 or as a
GTK window when a session exists; --cli drives the same controller from a TTY.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))

from aether_core.config import atomic_write_json, load_yaml  # noqa: E402
from aether_core import logging_setup  # noqa: E402

STATE_FILE = Path("/var/lib/aether/firstboot-state.json")
PAGES = ["locale", "keyboard", "timezone", "account", "network", "privacy",
         "encryption_status", "optional_ai", "completion"]
log = logging_setup.configure_logging("firstboot")


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"version": 1, "completed_pages": [], "choices": {}}


def save_state(state: dict) -> None:
    from datetime import datetime, timezone
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_write_json(STATE_FILE, state, mode=0o600)


def commit_page(state: dict, page: str, choices: dict) -> None:
    if page not in state["completed_pages"]:
        state["completed_pages"].append(page)
    state["choices"].update(choices)
    save_state(state)
    log.info(f"page committed: {page}")


def next_page(state: dict) -> str | None:
    for page in PAGES:
        if page not in state["completed_pages"]:
            return page
    return None


def finish(state: dict) -> None:
    state["completed_pages"] = PAGES[:]
    save_state(state)
    marker = Path("/var/lib/aether/firstboot-complete")
    marker.write_text("1\n")
    log.info("first boot setup complete")


def run_cli() -> int:
    """TTY driver: same controller, no GTK required."""
    state = load_state()
    page = next_page(state)
    while page:
        print(f"\n=== Aether first-boot setup: {page} ===")
        module = __import__(f"{page}_setup")
        choices = module.run_cli_prompt()  # each module implements run_cli_prompt()
        commit_page(state, page, choices)
        page = next_page(state)
    finish(state)
    print("\nSetup complete. Welcome to Aether.")
    return 0


def run_gtk() -> int:
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
    except (ImportError, ValueError):
        print("GTK unavailable; falling back to TTY setup", file=sys.stderr)
        return run_cli()

    state = load_state()

    class Wizard(Gtk.Window):
        def __init__(self):
            super().__init__(title="Aether — Welcome")
            self.set_default_size(640, 420)
            self.stack = Gtk.Stack()
            self.state = state
            for page in PAGES:
                self.stack.add_named(self._page_widget(page), page)
            self.add(self.stack)
            self._show(next_page(state))

        def _page_widget(self, page: str):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            box.set_border_width(24)
            title = Gtk.Label(label=f"Aether setup — {page}")
            title.get_style_context().add_class("eyebrow")
            box.pack_start(title, False, False, 0)
            module = __import__(f"{page}_setup")
            widget = module.gtk_widget(self._on_commit)
            box.pack_start(widget, True, True, 0)
            return box

        def _on_commit(self, page: str, choices: dict):
            commit_page(self.state, page, choices)
            nxt = next_page(self.state)
            if nxt:
                self._show(nxt)
            else:
                finish(self.state)
                Gtk.main_quit()

        def _show(self, page: str | None):
            if page is None:
                finish(self.state)
                Gtk.main_quit()
                return
            self.stack.set_visible_child_name(page)

    w = Wizard()
    w.show_all()
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(run_gtk() if "--gtk" in sys.argv or __import__("os").environ.get("DISPLAY") or __import__("os").environ.get("WAYLAND_DISPLAY") else run_cli())
