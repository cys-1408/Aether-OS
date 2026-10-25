"""Recovery drafts: offer restored drafts on start; never overwrite silently."""

from __future__ import annotations

import datetime
import re
from pathlib import Path

from gi.repository import Gtk

from app_framework.app_lifecycle import drafts_dir

_SOURCE_RE = re.compile(r"^source: (.*)$", re.MULTILINE)
_SAVED_RE = re.compile(r"^saved: (.*)$", re.MULTILINE)


def parse_draft(path: Path) -> dict:
    """Split a draft file into metadata and body (real parse, honest errors)."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"path": path, "body": "", "source": "", "saved": "", "error": str(exc)}
    source, saved = "", ""
    if raw.startswith("<!-- aether-writer draft"):
        match = _SOURCE_RE.search(raw)
        source = match.group(1).strip() if match else ""
        match = _SAVED_RE.search(raw)
        saved = match.group(1).strip() if match else ""
        end = raw.find("-->", 4)
        body = raw[end + 3:].lstrip("\n") if end != -1 else raw
    else:
        body = raw
    return {"path": path, "body": body, "source": source, "saved": saved, "error": ""}


class RecoveryDraftsDialog(Gtk.Dialog):
    """Lists recovered drafts with per-item Restore / Discard choices."""

    def __init__(self, parent, on_restore) -> None:
        super().__init__(
            title="Recovered drafts", transient_for=parent, modal=True
        )
        self.set_default_size(560, 380)
        self._on_restore = on_restore

        label = Gtk.Label(
            xalign=0,
            label="These drafts were autosaved by Writer. Restoring opens a copy — "
                  "nothing is overwritten without an explicit save by you.",
        )
        label.set_line_wrap(True)
        self.get_content_area().pack_start(label, False, False, 8)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        self._list_box = Gtk.ListBox()
        self._list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        scroll.add(self._list_box)
        self.get_content_area().pack_start(scroll, True, True, 4)

        self._drafts = []
        for entry in sorted(drafts_dir().glob("*.md")):
            parsed = parse_draft(entry)
            if not parsed["body"].strip() and not parsed["error"]:
                continue
            self._drafts.append(parsed)
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, margin=8)
            title = Gtk.Label(
                xalign=0,
                label=Path(parsed["source"]).name if parsed["source"] else entry.name,
            )
            subtitle = Gtk.Label(
                xalign=0,
                label=self._subtitle(parsed),
            )
            subtitle.get_style_context().add_class("aether-muted")
            box.pack_start(title, False, False, 0)
            box.pack_start(subtitle, False, False, 0)
            row.add(box)
            self._list_box.add(row)
        self._list_box.show_all()

        self.add_button("Close", Gtk.ResponseType.CLOSE)
        restore_btn = self.add_button("Restore selected", Gtk.ResponseType.APPLY)
        restore_btn.get_style_context().add_class("btn-orange")
        discard_btn = self.add_button("Discard selected", Gtk.ResponseType.REJECT)
        discard_btn.get_style_context().add_class("btn-dark")
        self.connect("response", self._on_response)

    @staticmethod
    def _subtitle(parsed: dict) -> str:
        if parsed["error"]:
            return f"unreadable: {parsed['error']}"
        saved = parsed["saved"] or "unknown time"
        stamp = saved.replace("T", " ")[:16] if saved else ""
        try:
            when = datetime.datetime.fromisoformat(saved).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            when = stamp
        words = len(parsed["body"].split())
        origin = parsed["source"] or "unsaved document"
        return f"from {origin} • saved {when} • {words} words"

    def _selected_draft(self):
        row = self._list_box.get_selected_row()
        if row is None:
            return None
        index = row.get_index()
        if 0 <= index < len(self._drafts):
            return self._drafts[index]
        return None

    def _on_response(self, dialog, response):
        selected = self._selected_draft()
        if response == Gtk.ResponseType.APPLY and selected:
            self._on_restore(selected)
            dialog.destroy()
        elif response == Gtk.ResponseType.REJECT and selected:
            confirm = Gtk.MessageDialog(
                transient_for=dialog, modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text=f"Discard draft “{Path(selected['path']).name}”?",
            )
            confirm.format_secondary_text(
                "The draft file will be deleted from ~/.local/share/aether/drafts."
            )
            answer = confirm.run()
            confirm.destroy()
            if answer == Gtk.ResponseType.OK:
                try:
                    selected["path"].unlink()
                except OSError as exc:
                    error = Gtk.MessageDialog(
                        transient_for=dialog, modal=True,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.CLOSE,
                        text="Could not delete draft",
                    )
                    error.format_secondary_text(str(exc))
                    error.run()
                    error.destroy()
                    return
                dialog.destroy()
                self.__class__(dialog.get_transient_for(), self._on_restore).show()
        else:
            dialog.destroy()
