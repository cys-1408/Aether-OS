"""Hardware requirements screen: honest probe results, hard gate on failure."""

from __future__ import annotations

from .base_screen import ScreenBase

MIN_RAM_MIB = 4 * 1024


def _format_probe(probe: dict) -> list[str]:
    ram = probe.get("ram_mib")
    ram_text = f"{ram} MiB" if isinstance(ram, (int, float)) else "unavailable"
    return [
        ("Architecture", probe.get("arch") or "unknown",
         probe.get("arch_ok", False)),
        ("Boot mode", "UEFI" if probe.get("uefi_ok") else "not UEFI / unknown",
         probe.get("uefi_ok", False)),
        ("Memory", ram_text, probe.get("ram_ok", False)),
    ]


class HardwareRequirementsScreen(ScreenBase):
    title = "Hardware check"
    subtitle = ("AetherOS requires x86_64, UEFI boot and at least 4 GiB RAM. "
                "Results below are measured on this machine, not assumed.")

    def _build_gtk(self):
        from gi.repository import Gtk

        probe = self.controller.hardware_probe()
        self.controller.apply("hardware_probe", probe)
        self.controller.apply("hardware_acknowledged",
                              bool(probe.get("requirements_met")) and
                              bool(self.controller.get("hardware_acknowledged")))

        box = self.gtk_box(spacing=12)
        box.pack_start(self.gtk_heading(), False, False, 0)

        grid = Gtk.Grid(column_spacing=16, row_spacing=6)
        for row, (name, value, passed) in enumerate(_format_probe(probe)):
            grid.attach(Gtk.Label(label=name, xalign=0.0), 0, row, 1, 1)
            grid.attach(Gtk.Label(label=value, xalign=0.0), 1, row, 1, 1)
            mark = "PASS" if passed else "FAIL"
            color = "#1a7f37" if passed else "#b3261e"
            grid.attach(Gtk.Label(
                label=f"<span foreground='{color}' weight='bold'>{mark}</span>",
                use_markup=True, xalign=0.0), 2, row, 1, 1)
        box.pack_start(grid, False, False, 0)

        requirements_met = bool(probe.get("requirements_met"))
        check = Gtk.CheckButton(
            label="I reviewed the hardware results"
            + ("" if requirements_met
               else " (requirements are NOT met; installation cannot continue)")
        )
        check.set_sensitive(requirements_met)
        check.set_active(requirements_met)
        check.connect("toggled", self._on_toggle)
        box.pack_start(check, False, False, 0)
        return box

    def _on_toggle(self, check):
        self.controller.apply("hardware_acknowledged", check.get_active())

    def run_cli(self) -> None:
        self.cli_header()
        probe = self.controller.hardware_probe()
        self.controller.apply("hardware_probe", probe)
        for name, value, passed in _format_probe(probe):
            self.cli_print(f"  {name:<14} {value:<24} [{'PASS' if passed else 'FAIL'}]")
        if not probe.get("requirements_met"):
            self.cli_print(
                "Hardware requirements are not met. Installation cannot continue."
            )
            self.controller.apply("hardware_acknowledged", False)
            return
        acknowledged = self.cli_confirm("I reviewed the hardware results",
                                        default=True)
        self.controller.apply("hardware_acknowledged", acknowledged)
