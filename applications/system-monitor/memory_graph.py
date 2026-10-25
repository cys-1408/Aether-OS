import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Memory graph from /proc/meminfo (real values)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import cairo


class MemoryGraph(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_size_request(220, 90)
        self.samples: list[float] = [0.0] * 60
        GLib.timeout_add_seconds(1, self._tick)
        self.connect("draw", self._draw)
        self._read()

    def _read(self) -> tuple[float, float]:
        total = avail = 0
        try:
            with open("/proc/meminfo") as fh:
                for line in fh:
                    if line.startswith("MemTotal:"):
                        total = int(line.split()[1])
                    elif line.startswith("MemAvailable:"):
                        avail = int(line.split()[1])
        except (OSError, ValueError):
            pass
        return total, avail

    def _tick(self):
        total, avail = self._read()
        used = 1 - (avail / total) if total else 0
        self.samples.append(max(0.0, min(1.0, used)))
        self.samples = self.samples[-60:]
        self.queue_draw()
        return True

    def _draw(self, _w, cr: cairo.Context):
        w = self.get_allocated_width()
        h = self.get_allocated_height()
        cr.set_source_rgb(0.96, 0.94, 0.90)
        cr.rectangle(0, 0, w, h)
        cr.fill()
        cr.set_source_rgb(0.49, 0.56, 0.50)
        n = len(self.samples)
        for i, v in enumerate(self.samples):
            bh = v * (h - 8)
            cr.rectangle(i * (w / 60), h - bh, max(1, w / 60 - 1), bh)
        cr.fill()
        total, avail = self._read()
        cr.set_source_rgb(0.29, 0.28, 0.24)
        cr.set_font_size(11)
        cr.show_text(f"mem {avail//1024} MB free / {total//1024} MB")
        return False
