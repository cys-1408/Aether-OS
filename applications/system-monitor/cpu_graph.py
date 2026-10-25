import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""CPU graph: real /proc/stat deltas drawn with cairo."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import cairo


class CpuGraph(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_size_request(220, 90)
        self.samples: list[float] = [0.0] * 60
        self._last = self._read()
        GLib.timeout_add_seconds(1, self._tick)
        self.connect("draw", self._draw)

    @staticmethod
    def _read() -> tuple[int, int]:
        try:
            with open("/proc/stat") as fh:
                parts = fh.readline().split()[1:]
            vals = list(map(int, parts))
            return sum(vals), vals[3] + vals[4]
        except (OSError, ValueError):
            return 0, 0

    def _tick(self):
        total, idle = self._read()
        if total > self._last[0]:
            used = 1 - (idle - self._last[1]) / (total - self._last[0])
            self.samples.append(max(0.0, min(1.0, used)))
            self.samples = self.samples[-60:]
        self._last = (total, idle)
        self.queue_draw()
        return True

    def _draw(self, _w, cr: cairo.Context):
        w = self.get_allocated_width()
        h = self.get_allocated_height()
        cr.set_source_rgb(0.96, 0.94, 0.90)
        cr.rectangle(0, 0, w, h)
        cr.fill()
        cr.set_source_rgb(0.85, 0.51, 0.31)
        n = len(self.samples)
        for i, v in enumerate(self.samples):
            bh = v * (h - 8)
            cr.rectangle(i * (w / 60), h - bh, max(1, w / 60 - 1), bh)
        cr.fill()
        return False
