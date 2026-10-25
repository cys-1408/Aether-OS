"""Install progress screen: runs the transaction and streams its events."""

from __future__ import annotations

import queue
import threading

from ...install.install_transaction import InstallTransaction
from .base_screen import ScreenBase


class InstallProgressScreen(ScreenBase):
    title = "Installing"
    subtitle = ("Installing AetherOS to the target disk. Do not power off the "
                "machine. The log streams below.")

    def __init__(self, controller):
        super().__init__(controller)
        self.events: "queue.Queue[dict]" = queue.Queue()
        self.worker: threading.Thread | None = None
        self.result: dict | None = None

    # ------------------------------------------------------------------ #
    def start(self) -> None:
        """Run the transaction in a background thread (GTK mode) or inline."""
        if self.worker is not None:
            return
        if self._gtk_mode():
            self.worker = threading.Thread(target=self._run_inline, daemon=True)
            self.worker.start()
        else:
            self._run_inline()

    def _gtk_mode(self) -> bool:
        from .base_screen import GTK_AVAILABLE

        return GTK_AVAILABLE

    def _run_inline(self) -> None:
        transaction = InstallTransaction(
            self.controller, progress_cb=self.events.put)
        self.result = transaction.run()
        self.events.put({"event": "transaction_result", "result": self.result})

    def drain_events(self) -> list[dict]:
        """Poll all pending progress events (GTK timer calls this)."""
        events = []
        while True:
            try:
                events.append(self.events.get_nowait())
            except queue.Empty:
                break
        return events

    # GTK ---------------------------------------------------------------
    def _build_gtk(self):
        from gi.repository import GLib, Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        status = Gtk.Label(xalign=0.0)
        status.set_text("starting…")
        box.pack_start(status, False, False, 0)

        view = Gtk.TextView(editable=False, cursor_visible=False,
                            monospace=True)
        view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        scroll = Gtk.ScrolledWindow(shadow_type=Gtk.ShadowType.IN)
        scroll.set_vexpand(True)
        scroll.set_min_content_height(320)
        scroll.add(view)
        box.pack_start(scroll, True, True, 0)

        spinner = Gtk.Spinner(active=True)
        box.pack_start(spinner, False, False, 0)

        buffer = view.get_buffer()
        end_mark = buffer.create_mark("end", buffer.get_end_iter(), False)

        def append_line(line: str) -> None:
            buffer.insert(buffer.get_end_iter(), line + "\n")
            view.scroll_mark_onscreen(end_mark, 0.0)

        def poll() -> bool:
            events = self.drain_events()
            for event in events:
                kind = event.get("event")
                if kind == "step_started":
                    append_line(f">> {event.get('step')} started")
                    status.set_text(f"step: {event.get('step')}")
                elif kind == "step_finished":
                    append_line(f"   ok ({event.get('duration_s', 0):.1f}s)")
                elif kind == "step_failed":
                    append_line(f"   FAILED: {event.get('error')}")
                elif kind == "failed":
                    append_line("install failed; see failure recovery options")
                    spinner.stop()
                elif kind == "rollback_finished":
                    append_line("rollback finished")
                elif kind == "done":
                    append_line("install completed successfully")
                    spinner.stop()
                    status.set_text("done")
            return True

        GLib.timeout_add(200, poll)
        self.start()
        return box

    # CLI ---------------------------------------------------------------
    def run_cli(self) -> None:
        self.cli_header()
        self.start()
        import time

        done_events = {"done", "failed", "transaction_result"}
        seen_result = False
        while not (seen_result and self.events.empty()):
            try:
                event = self.events.get(timeout=0.5)
            except queue.Empty:
                continue
            kind = event.get("event")
            if kind == "step_started":
                self.cli_print(f">> {event.get('step')} started")
            elif kind == "step_finished":
                self.cli_print(f"   ok ({event.get('duration_s', 0):.1f}s)")
            elif kind == "step_failed":
                self.cli_print(f"   FAILED: {event.get('error')}")
            elif kind == "failed":
                self.cli_print("install failed")
            elif kind == "rollback_finished":
                self.cli_print("rollback finished")
            elif kind == "done":
                self.cli_print("install completed successfully")
            elif kind in done_events and kind == "transaction_result":
                seen_result = True
        if self.result and self.result.get("status") != "complete":
            time.sleep(0.1)
