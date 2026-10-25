"""Cell-metrics based resize handling for the fallback terminal renderer."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk, Pango


class CellMetrics:
    """Measures the real cell size of the terminal font via Pango."""

    def __init__(self, font_desc: Pango.FontDescription) -> None:
        self.font_desc = font_desc
        self.char_width = 9.0
        self.char_height = 18.0
        self._measure()

    def _measure(self) -> None:
        offscreen = Gtk.OffscreenWindow()
        label = Gtk.Label()
        layout = label.create_pango_layout("M")
        layout.set_font_description(self.font_desc)
        _ink, logical = layout.get_pixel_size()
        if logical.width > 0:
            self.char_width = float(logical.width)
        context = label.get_pango_context()
        font_metrics = context.get_metrics(self.font_desc)
        ascent = font_metrics.get_ascent() / Pango.SCALE
        descent = font_metrics.get_descent() / Pango.SCALE
        height = ascent + descent
        if height > 0:
            self.char_height = float(height)
        offscreen.destroy()


class ResizeCoordinator:
    """Turns widget allocations into pty (cols, rows) updates."""

    def __init__(self, widget: Gtk.Widget, font_desc: Pango.FontDescription,
                 on_resize) -> None:
        self.metrics = CellMetrics(font_desc)
        self._widget = widget
        self._on_resize = on_resize
        self._last = (0, 0)
        widget.connect("size-allocate", self._on_allocate)

    def _on_allocate(self, _widget, allocation):
        cols = int(allocation.width / self.metrics.char_width)
        rows = int(allocation.height / self.metrics.char_height)
        cols = max(cols, 4)
        rows = max(rows, 3)
        if (cols, rows) != self._last:
            self._last = (cols, rows)
            self._on_resize(cols, rows)

    def current(self):
        return self._last


def terminal_font(size_points: float = 11.5) -> Pango.FontDescription:
    description = Pango.FontDescription()
    description.set_family("monospace")
    description.set_size(int(size_points * Pango.SCALE))
    return description


def screen_geometry():
    """Best-effort screen size for default window sizing."""
    display = Gdk.Display.get_default()
    if display is None:
        return (1024, 700)
    monitor = display.get_primary_monitor() or display.get_monitor(0)
    if monitor is None:
        return (1024, 700)
    geometry = monitor.get_geometry()
    return (geometry.width, geometry.height)
