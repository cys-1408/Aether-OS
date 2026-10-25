"""Local AI assist for Writer: Summarize via Runtime.infer (honest gating).

The button is disabled with a truthful tooltip whenever the Runtime service
is unreachable. Results are shown in a review dialog and inserted only after
the user approves — never applied silently.
"""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

MAX_INFER_CHARS = 8000


class LocalAiAssist:
    """Wires the Summarize flow to the Runtime service."""

    def __init__(self, services, parent_window: Gtk.Window) -> None:
        self._services = services
        self._parent = parent_window
        self._dialog = None

    def refresh_button_state(self, button: Gtk.Button, text_len: int) -> None:
        """Keep the button honest: disabled with a reason when it cannot run."""
        if not self._services.available("Runtime"):
            button.set_sensitive(False)
            button.set_tooltip_text(
                "Runtime service unavailable — local AI assist needs the "
                "aether-runtime service socket."
            )
            return
        if text_len < 80:
            button.set_sensitive(False)
            button.set_tooltip_text("Write at least a few sentences to summarize.")
            return
        button.set_sensitive(True)
        button.set_tooltip_text("Summarize the document with the local model")

    def summarize(self, document_text: str, on_insert) -> None:
        text = document_text[:MAX_INFER_CHARS]
        self._dialog = self._progress_dialog()
        params = {
            "prompt": (
                "Summarize the following document in 3-5 concise sentences. "
                "Reply with the summary only.\n\n" + text
            ),
            "max_tokens": 300,
        }

        def on_result(result):
            summary = self._extract_text(result)
            GLib.idle_add(self._finish, summary, on_insert)

        def on_error(error):
            GLib.idle_add(self._fail, str(error))

        self._services.call_async(
            "Runtime", "infer", params, on_result, on_error, timeout=120.0
        )

    @staticmethod
    def _extract_text(result) -> str:
        if not isinstance(result, dict):
            return ""
        for key in ("text", "content", "output", "response"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        nested = result.get("result") or result.get("response")
        if isinstance(nested, dict):
            for key in ("text", "content", "output"):
                value = nested.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return ""

    def _progress_dialog(self) -> Gtk.Dialog:
        dialog = Gtk.Dialog(title="Summarizing…", transient_for=self._parent, modal=True)
        dialog.get_content_area().pack_start(
            Gtk.Label(label="Asking the local Runtime model — this can take a moment."),
            False, False, 14,
        )
        spinner = Gtk.Spinner()
        spinner.start()
        dialog.get_content_area().pack_start(spinner, False, False, 6)
        dialog.get_content_area().show_all()
        dialog.show()
        return dialog

    def _finish(self, summary: str, on_insert):
        if self._dialog is not None:
            self._dialog.destroy()
            self._dialog = None
        if not summary:
            self._fail("The model returned no text (empty response).")
            return GLib.SOURCE_REMOVE
        dialog = Gtk.Dialog(
            title="Summary ready", transient_for=self._parent, modal=True
        )
        dialog.set_default_size(520, 320)
        label = Gtk.Label(
            xalign=0, label="Review the summary. It is inserted only if you approve:"
        )
        dialog.get_content_area().pack_start(label, False, False, 8)
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        view = Gtk.TextView()
        view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        view.get_buffer().set_text(summary)
        view.set_editable(False)
        scroll.add(view)
        dialog.get_content_area().pack_start(scroll, True, True, 4)
        dialog.add_button("Discard", Gtk.ResponseType.CANCEL)
        insert_btn = dialog.add_button("Insert at cursor", Gtk.ResponseType.OK)
        insert_btn.get_style_context().add_class("btn-orange")
        dialog.get_content_area().show_all()

        def on_response(_dialog, response):
            if response == Gtk.ResponseType.OK:
                on_insert(summary + "\n\n")
            _dialog.destroy()

        dialog.connect("response", on_response)
        dialog.show()
        return GLib.SOURCE_REMOVE

    def _fail(self, message: str):
        if self._dialog is not None:
            self._dialog.destroy()
            self._dialog = None
        error = Gtk.MessageDialog(
            transient_for=self._parent, modal=True,
            message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CLOSE,
            text="Summarize failed",
        )
        error.format_secondary_text(message)
        error.run()
        error.destroy()
        return GLib.SOURCE_REMOVE
