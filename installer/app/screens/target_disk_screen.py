"""Target disk selection with an explicit destructive warning."""

from __future__ import annotations

from ...storage.disk_discovery import discover_disks, disk_summary, human_size
from .base_screen import ScreenBase


class TargetDiskScreen(ScreenBase):
    title = "Target disk"
    subtitle = ("Choose the disk where AetherOS will be installed. EVERYTHING "
                "on the selected disk will be erased in a later step.")

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        disks = discover_disks()
        self.controller.apply("discovered_disks", disks)
        if not disks:
            empty = Gtk.Label(xalign=0.0)
            empty.set_markup(
                "<span foreground='#b3261e'>No disks detected. Installation "
                "cannot continue.</span>"
            )
            box.pack_start(empty, False, False, 0)
            return box

        warning = Gtk.Label(xalign=0.0)
        warning.set_markup(
            "<span foreground='#b3261e' weight='bold'>Destructive: all data "
            "on the chosen disk will be destroyed.</span>"
        )
        box.pack_start(warning, False, False, 0)

        listbox = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        for disk in disks:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12,
                           margin_top=6, margin_bottom=6, margin_start=10,
                           margin_end=10)
            removable = " [REMOVABLE]" if disk.get("removable") else ""
            hbox.pack_start(Gtk.Label(
                label=f"<b>{disk['path']}</b> — {disk.get('model') or 'model unknown'}"
                      f"{removable}", use_markup=True, xalign=0.0), True, True, 0)
            hbox.pack_start(Gtk.Label(
                label=human_size(disk.get("size"))), False, False, 0)
            row.add(hbox)
            listbox.add(row)
        scroll = Gtk.ScrolledWindow(shadow_type=Gtk.ShadowType.IN)
        scroll.set_min_content_height(220)
        scroll.add(listbox)
        box.pack_start(scroll, True, True, 0)

        def on_selected(_listbox, row):
            if row is None:
                return
            index = row.get_index()
            disk = disks[index]
            self.controller.apply("target_disk", disk["path"])
            self.controller.apply("target_disk_info", disk)
            detail.set_markup(
                "<span foreground='#b3261e'>Will ERASE: "
                f"{disk_summary(disk)}</span>"
            )

        listbox.connect("row-selected", on_selected)
        detail = Gtk.Label(xalign=0.0)
        detail.set_line_wrap(True)
        box.pack_start(detail, False, False, 0)

        preselected = self.controller.get("target_disk")
        if preselected:
            for index, disk in enumerate(disks):
                if disk["path"] == preselected:
                    listbox.select_row(listbox.get_row_at_index(index))
                    break
        return box

    def run_cli(self) -> None:
        self.cli_header()
        disks = discover_disks()
        self.controller.apply("discovered_disks", disks)
        if not disks:
            self.cli_print("No disks detected. Installation cannot continue.")
            return
        self.cli_print("WARNING: all data on the chosen disk will be destroyed.")
        for index, disk in enumerate(disks, start=1):
            removable = " [REMOVABLE]" if disk.get("removable") else ""
            self.cli_print(f"  {index}) {disk_summary(disk)}{removable}")
        while True:
            raw = input(f"Select disk 1-{len(disks)}: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(disks):
                break
            self.cli_print("  invalid choice")
        disk = disks[int(raw) - 1]
        self.controller.apply("target_disk", disk["path"])
        self.controller.apply("target_disk_info", disk)
        self.cli_print(f"Will ERASE: {disk_summary(disk)}")
