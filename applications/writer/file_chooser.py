"""File chooser dialogs for Writer (open/save with .md/.txt filters)."""

from __future__ import annotations

from pathlib import Path

from gi.repository import Gtk

from document_model import SUPPORTED_EXTENSIONS

MD_FILTER_TEXT = "Markdown and text (*.md, *.txt)"
ALL_TEXT = "All files"


def open_dialog(parent) -> Path | None:
    chooser = Gtk.FileChooserDialog(
        title="Open document", transient_for=parent,
        action=Gtk.FileChooserAction.OPEN,
        buttons=("Cancel", Gtk.ResponseType.CANCEL, "Open", Gtk.ResponseType.OK),
    )
    md_filter = Gtk.FileFilter()
    md_filter.set_name(MD_FILTER_TEXT)
    for ext in SUPPORTED_EXTENSIONS:
        md_filter.add_pattern(f"*{ext}")
    chooser.add_filter(md_filter)
    any_filter = Gtk.FileFilter()
    any_filter.set_name(ALL_TEXT)
    any_filter.add_pattern("*")
    chooser.add_filter(any_filter)
    chooser.set_current_folder(str(Path.home() / "Documents"))
    answer = chooser.run()
    chosen = chooser.get_filename()
    chooser.destroy()
    if answer == Gtk.ResponseType.OK and chosen:
        return Path(chosen)
    return None


def save_dialog(parent, suggested_name: str = "Untitled.md") -> Path | None:
    chooser = Gtk.FileChooserDialog(
        title="Save document", transient_for=parent,
        action=Gtk.FileChooserAction.SAVE,
        buttons=("Cancel", Gtk.ResponseType.CANCEL, "Save", Gtk.ResponseType.OK),
    )
    md_filter = Gtk.FileFilter()
    md_filter.set_name(MD_FILTER_TEXT)
    for ext in SUPPORTED_EXTENSIONS:
        md_filter.add_pattern(f"*{ext}")
    chooser.add_filter(md_filter)
    chooser.set_current_folder(str(Path.home() / "Documents"))
    chooser.set_current_name(suggested_name)
    answer = chooser.run()
    chosen = chooser.get_filename()
    chooser.destroy()
    if answer == Gtk.ResponseType.OK and chosen:
        target = Path(chosen)
        if target.suffix.lower() not in SUPPORTED_EXTENSIONS:
            target = target.with_suffix(".md")
        return target
    return None
