"""Partition plan screen: automatic (ESP 1 GiB + root) or basic manual."""

from __future__ import annotations

from ...storage.partition_planner import (
    TYPE_LINUX,
    TYPE_LINUX_X86_64,
    TYPE_EFI,
    build_auto_plan,
    canonical_plan_hash,
    plan_summary_lines,
)
from .base_screen import ScreenBase

GIB = 1024 ** 3
MIB = 1024 ** 2


class PartitionPlanScreen(ScreenBase):
    title = "Partitioning"
    subtitle = ("Automatic layout: 1 GiB EFI system partition + root using the "
                "rest of the disk. Manual mode creates a basic custom layout.")

    def _build_gtk(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        radio_auto = Gtk.RadioButton.with_label_from_widget(
            None, "Automatic: ESP 1 GiB + root (rest of disk)")
        radio_manual = Gtk.RadioButton.with_label_from_widget(
            radio_auto, "Manual: ESP + custom root size (GiB)")
        mode = self.controller.get("partition_plan", {}).get("mode", "auto")
        (radio_manual if mode == "manual" else radio_auto).set_active(True)
        box.pack_start(radio_auto, False, False, 0)
        box.pack_start(radio_manual, False, False, 0)

        size_grid = Gtk.Grid(column_spacing=10, row_spacing=6, margin_start=20)
        size_grid.attach(Gtk.Label(label="Root size (GiB)", xalign=0.0), 0, 0, 1, 1)
        root_size = Gtk.SpinButton.new_with_range(20, 10240, 1)
        existing = self.controller.get("manual_root_gib", 64)
        root_size.set_value(float(existing))
        size_grid.attach(root_size, 1, 0, 1, 1)
        box.pack_start(size_grid, False, False, 0)

        preview = Gtk.Label(xalign=0.0)
        preview.set_line_wrap(True)
        box.pack_start(preview, False, False, 0)

        def regenerate(_widget=None):
            plan = self._current_plan(radio_auto.get_active(),
                                      int(root_size.get_value()))
            if plan is None:
                preview.set_markup("<span foreground='#b3261e'>disk not "
                                   "selected yet</span>")
                return
            self.controller.apply("partition_plan", plan)
            self.controller.apply("manual_root_gib", int(root_size.get_value()))
            preview.set_markup("\n".join(plan_summary_lines(plan)))

        radio_auto.connect("toggled", regenerate)
        radio_manual.connect("toggled", regenerate)
        root_size.connect("value-changed", regenerate)
        regenerate()
        return box

    def _current_plan(self, auto: bool, root_gib: int):
        disk = self.controller.get("target_disk")
        info = self.controller.get("target_disk_info", {})
        disk_size = info.get("size")
        encrypted = bool(self.controller.get("encryption_enabled"))
        if auto:
            if not disk or not disk_size:
                return None
            return build_auto_plan(disk, int(disk_size), encrypted=encrypted)
        if not disk or not disk_size:
            return None
        root_bytes = max(20, root_gib) * GIB
        esp_bytes = 1 * GIB
        if root_bytes + esp_bytes + MIB > int(disk_size):
            root_bytes = int(disk_size) - esp_bytes - MIB
        plan = {
            "version": 1,
            "disk": disk,
            "mode": "manual",
            "label": "gpt",
            "firmware": "uefi",
            "encrypted": encrypted,
            "partitions": [
                {"name": "esp", "role": "esp", "size_bytes": esp_bytes,
                 "type": TYPE_EFI, "filesystem": "vfat", "label": "AETHER-ESP",
                 "mount": "/efi"},
                {"name": "root", "role": "root", "size_bytes": root_bytes,
                 "type": TYPE_LINUX_X86_64 if not encrypted else TYPE_LINUX,
                 "filesystem": "ext4", "label": "AETHEROS", "mount": "/",
                 "encrypted": encrypted},
            ],
        }
        plan["plan_hash"] = canonical_plan_hash(plan)
        return plan

    def run_cli(self) -> None:
        self.cli_header()
        mode = self.cli_choose("Layout", ["auto", "manual"],
                               default="auto")
        root_gib = 64
        if mode == "manual":
            while True:
                raw = self.cli_ask("Root partition size in GiB (min 20)",
                                   default="64")
                if raw.isdigit() and int(raw) >= 20:
                    root_gib = int(raw)
                    break
                self.cli_print("  enter a number >= 20")
        auto = mode == "auto"
        plan = self._current_plan(auto, root_gib)
        while plan is None:
            self.cli_print("Select the target disk first; returning to disk "
                           "selection is required.")
            raise RuntimeError("partition plan requested without a target disk")
        self.controller.apply("partition_plan", plan)
        self.controller.apply("manual_root_gib", root_gib)
        for line in plan_summary_lines(plan):
            self.cli_print(line)
