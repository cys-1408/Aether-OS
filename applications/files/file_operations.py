"""File operations for Aether Files: copy/move/rename/trash/restore.

Copy and move run on a worker thread with a real progress dialog; name
conflicts open the policy dialog (skip / rename / overwrite-with-confirm).
Trash and restore delegate to ``aether_core.filesops`` (freedesktop Trash
spec implementation owned by the shared library).
"""

from __future__ import annotations

import os
import shutil
import threading
from pathlib import Path

from gi.repository import GLib, Gtk


class ConflictDecision:
    SKIP = "skip"
    RENAME = "rename"
    OVERWRITE = "overwrite"
    CANCEL = "cancel"


def _unique_name(directory: Path, name: str) -> str:
    candidate = directory / name
    if not candidate.exists():
        return name
    stem = candidate.stem
    suffix = candidate.suffix
    for counter in range(2, 1000):
        new_name = f"{stem} ({counter}){suffix}"
        if not (directory / new_name).exists():
            return new_name
    return name


class FileOperations:
    """Executes filesystem operations with visible, truthful progress."""

    def __init__(self, parent_window: Gtk.Window, services=None) -> None:
        self._parent = parent_window
        self._services = services
        self._cancel = threading.Event()

    # -- trash ---------------------------------------------------------------

    def move_to_trash(self, paths) -> str:
        """Trash via aether_core.filesops; raises RuntimeError when absent."""
        try:
            from aether_core.filesops import trash
        except Exception as exc:
            raise RuntimeError(f"Trash unavailable (aether_core.filesops missing): {exc}") from exc
        last = ""
        for path in paths:
            result = trash(Path(path))
            last = str(result.get("trashed_to", path))
        return last

    def list_trash(self) -> list:
        try:
            from aether_core.filesops import list_trash
        except Exception as exc:
            raise RuntimeError(f"Trash unavailable (aether_core.filesops missing): {exc}") from exc
        return list(list_trash())

    def restore_from_trash(self, trash_name: str) -> str:
        try:
            from aether_core.filesops import restore
        except Exception as exc:
            raise RuntimeError(f"Trash unavailable (aether_core.filesops missing): {exc}") from exc
        result = restore(trash_name)
        return str(result.get("restored_to", result.get("restored", trash_name)))

    def delete_from_trash(self, trash_name: str) -> None:
        """Permanently delete one trash entry (destructive, caller confirms)."""
        trash_dir = Path.home() / ".local" / "share" / "Trash"
        removed = False
        for sub in ("files", "info"):
            candidate = trash_dir / sub / trash_name
            if candidate.is_dir() and sub == "files":
                shutil.rmtree(candidate, ignore_errors=False)
                removed = True
            elif candidate.is_file():
                candidate.unlink()
                removed = True
        if not removed:
            raise RuntimeError(f"Trash entry not found: {trash_name}")

    # -- rename ---------------------------------------------------------------

    @staticmethod
    def rename(path: Path, new_name: str) -> Path:
        if not new_name or "/" in new_name or new_name in (".", ".."):
            raise ValueError(f"Invalid name: {new_name!r}")
        target = path.parent / new_name
        if target.exists():
            raise FileExistsError(f"Name already exists: {new_name}")
        os.rename(path, target)
        return target

    # -- copy / move with progress -------------------------------------------

    def transfer(self, sources, dest_dir: Path, move: bool, on_done, on_error) -> None:
        """Run a copy/move on a thread; show a progress dialog until finished."""
        self._cancel.clear()
        dialog, progress_bar, status_label = self._make_progress_dialog(move)
        total = self._measure(sources)
        state = {"done": 0, "policy": None, "apply_all": False, "cancelled": False}
        errors = []

        def report(done, current_name):
            GLib.idle_add(self._update_progress, dialog, progress_bar, status_label,
                          done, total, current_name)

        def ask_conflict(name: str):
            answer = {}

            def decide():
                answer.update(self._conflict_dialog(name, state["apply_all"]))
                GLib.idle_add(loop_quit)

            def loop_quit():
                if "loop" in answer:
                    answer["loop"].quit()
                return GLib.SOURCE_REMOVE

            loop = GLib.MainLoop()
            answer["loop"] = loop
            GLib.idle_add(decide)
            loop.run()
            return answer

        def worker():
            try:
                for source in sources:
                    if self._cancel.is_set():
                        state["cancelled"] = True
                        break
                    source_path = Path(source)
                    if not source_path.exists():
                        errors.append(f"missing: {source_path}")
                        continue
                    target = dest_dir / source_path.name
                    if target.exists():
                        if state["apply_all"] and state["policy"] is not None:
                            decision = state["policy"]
                        else:
                            decision = ask_conflict(source_path.name)["decision"]
                            if decision is None or decision == ConflictDecision.CANCEL:
                                state["cancelled"] = True
                                break
                            state["policy"] = decision
                        if decision == ConflictDecision.SKIP:
                            continue
                        if decision == ConflictDecision.RENAME:
                            target = dest_dir / _unique_name(dest_dir, source_path.name)
                        elif decision == ConflictDecision.OVERWRITE:
                            confirm = self._confirm_overwrite(target)
                            if not confirm:
                                continue
                            if target.is_dir():
                                shutil.rmtree(target)
                            else:
                                target.unlink()
                    if move:
                        shutil.move(str(source_path), str(target))
                    else:
                        if source_path.is_dir():
                            shutil.copytree(source_path, target, dirs_exist_ok=True)
                        else:
                            shutil.copy2(source_path, target)
                    size = self._entry_size(source_path)
                    state["done"] += size
                    report(state["done"], source_path.name)
            except Exception as exc:  # surfaced honestly in the dialog
                errors.append(str(exc))
            finally:
                GLib.idle_add(self._finish_transfer, dialog, errors, state["cancelled"],
                              on_done, on_error)

        threading.Thread(target=worker, daemon=True).start()

    # -- internals -------------------------------------------------------------

    @staticmethod
    def _entry_size(path: Path) -> int:
        try:
            if path.is_file():
                return path.stat().st_size
            return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        except OSError:
            return 0

    def _measure(self, sources) -> int:
        return sum(self._entry_size(Path(s)) for s in sources) or 1

    def _make_progress_dialog(self, move: bool):
        title = "Moving files" if move else "Copying files"
        dialog = Gtk.Dialog(title=title, transient_for=self._parent, modal=True)
        dialog.set_default_size(380, 110)
        box = dialog.get_content_area()
        status_label = Gtk.Label(label="Preparing…", xalign=0)
        progress_bar = Gtk.ProgressBar()
        cancel_btn = dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        cancel_btn.connect("clicked", lambda _b: self._cancel.set())
        box.pack_start(status_label, False, False, 8)
        box.pack_start(progress_bar, False, False, 6)
        box.show_all()
        dialog.show()
        return dialog, progress_bar, status_label

    def _update_progress(self, dialog, bar, label, done, total, name):
        label.set_text(f"{name} — {done}/{total} bytes")
        bar.set_fraction(min(1.0, done / max(total, 1)))
        return GLib.SOURCE_REMOVE

    def _finish_transfer(self, dialog, errors, cancelled, on_done, on_error):
        dialog.destroy()
        if errors:
            on_error("; ".join(errors))
        else:
            on_done("cancelled" if cancelled else "ok")
        return GLib.SOURCE_REMOVE

    def _conflict_dialog(self, name: str, apply_all: bool) -> dict:
        dialog = Gtk.Dialog(
            title="Name conflict", transient_for=self._parent, modal=True
        )
        dialog.set_default_size(380, 130)
        label = Gtk.Label(label=f"An item named “{name}” already exists here.")
        dialog.get_content_area().pack_start(label, False, False, 10)
        grid = Gtk.Grid(column_spacing=8, row_spacing=8)
        options = [
            ("skip", "Skip"), ("rename", "Rename (keep both)"), ("overwrite", "Overwrite"),
        ]
        radios = {}
        for index, (value, text) in enumerate(options):
            radio = Gtk.RadioButton.new_with_label_from_widget(
                radios.get(options[0][1]) if index else None, text
            )
            radios[value] = radio
            grid.attach(radio, 0, index, 2, 1)
        apply_check = Gtk.CheckButton(label="Apply this action to all remaining conflicts")
        apply_check.set_active(apply_all)
        grid.attach(apply_check, 0, 3, 2, 1)
        dialog.get_content_area().pack_start(grid, False, False, 4)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Continue", Gtk.ResponseType.OK)
        dialog.get_content_area().show_all()
        decision = None
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            for value, radio in radios.items():
                if radio.get_active():
                    decision = value
                    break
        dialog.destroy()
        return {"decision": decision, "apply_all": apply_check.get_active()}

    def _confirm_overwrite(self, target: Path) -> bool:
        dialog = Gtk.MessageDialog(
            transient_for=self._parent, modal=True,
            message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Overwrite {target.name}?",
        )
        dialog.format_secondary_text("The existing item will be replaced permanently.")
        answer = dialog.run()
        dialog.destroy()
        return answer == Gtk.ResponseType.OK
