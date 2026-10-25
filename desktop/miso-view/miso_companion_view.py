import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""The animated Miso companion — SVG rendering + state machine + dragging."""
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Rsvg", "2.0")
from gi.repository import Gtk, GLib, Gdk
import cairo

try:
    gi.require_version("Rsvg", "2.0")
    from gi.repository import Rsvg
    HAS_RSVG = True
except (ImportError, ValueError):
    HAS_RSVG = False

ASSETS = Path(__file__).resolve().parents[1] / "assets/miso"
STATES = ("idle", "walking", "running", "jumping", "searching", "sleeping",
          "carrying", "pulling", "pushing", "focused")
FILE_BY_STATE = {
    "idle": "miso-idle.svg", "walking": "miso-walk.svg", "running": "miso-run.svg",
    "jumping": "miso-jump.svg", "searching": "miso-search.svg", "sleeping": "miso-sleep.svg",
    "carrying": "miso-carry.svg", "pulling": "miso.svg", "pushing": "miso.svg",
    "focused": "miso-focus.svg",
}


class MisoCompanionView(Gtk.Window):
    WIDTH, HEIGHT = 150, 135

    def __init__(self, shell):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.shell = shell
        self.set_decorated(False)
        self.set_size_request(self.WIDTH, self.HEIGHT)
        self.set_app_paintable(True)
        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK
                        | Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.state = "idle"
        self.reduced_motion = False
        self._phase = 0.0
        self._jump_t = 0.0
        self._drag = None
        self._handles = None
        if HAS_RSVG:
            self._handles = {s: Rsvg.Handle.new_from_file(str(ASSETS / FILE_BY_STATE[s]))
                             for s in STATES}
        try:
            screen = self.get_screen()
            self.visual = screen.get_rgba_visual()
            if self.visual:
                self.set_visual(self.visual)
        except Exception:
            self.visual = None
        self.drawing = Gtk.DrawingArea()
        self.drawing.connect("draw", self._on_draw)
        self.add(self.drawing)
        GLib.timeout_add(33, self._animate)  # ~30fps per motion.yaml
        self.connect("motion-notify-event", self._on_motion)
        self.connect("button-press-event", self._on_press)
        self.connect("button-release-event", self._on_release)
        self.connect("key-press-event", self._on_key)
        self.set_role("aether-miso")

    # ------------------------------------------------------------------ state
    def set_state(self, state: str):
        if state in STATES and state != self.state:
            self.state = state
            if state == "jumping":
                self._jump_t = 0.0
            self.drawing.queue_draw()

    def enable_reduced_motion(self):
        self.reduced_motion = True

    def stop(self):
        pass  # GLib timeout stops with the main loop

    # ------------------------------------------------------------------ drag
    def _on_press(self, w, event):
        self._drag = (event.x_root, event.y_root, event.x, event.y)
        self.get_window().set_cursor(Gdk.Cursor.new_from_name(self.get_display(), "grabbing"))

    def _on_motion(self, w, event):
        if self._drag is None:
            self._track_pupils(event)
            return
        _, _, ox, oy = self._drag
        px = int(event.x_root - ox)
        py = int(event.y_root - oy)
        pos = self.get_position()
        self.move(max(0, pos[0] + px), max(43, pos[1] + py))
        self._drag = (event.x_root, event.y_root, event.x, event.y)

    def _on_release(self, w, event):
        self._drag = None
        self.get_window().set_cursor(Gdk.Cursor.new_from_name(self.get_display(), "grab"))

    def _track_pupils(self, event):
        pass  # pupil tracking handled inside _animate using pointer position

    def _on_key(self, w, event):
        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_space:
            self.shell.controller.on_miso_clicked()
            return True
        return False

    # ------------------------------------------------------------------ render
    def _animate(self):
        if not self.reduced_motion:
            self._phase = (self._phase + 1) % 1000
            if self.state == "jumping":
                self._jump_t = min(1.0, self._jump_t + 1 / 21.5)  # .65s @30fps
                if self._jump_t >= 1.0:
                    self.set_state("idle")
            self.drawing.queue_draw()
        return True

    def _on_draw(self, widget, cr):
        if not self._handles:
            cr.set_source_rgb(0.95, 0.92, 0.86)
            cr.rectangle(0, 0, self.WIDTH, self.HEIGHT)
            cr.fill()
            return
        cr.save()
        import math
        bob = 0.0
        if self.state in ("walking", "running") and not self.reduced_motion:
            freq = 0.3 if self.state == "running" else 0.5
            bob = -4 * abs(math.sin(self._phase * freq))
        elif self.state == "jumping":
            t = self._jump_t
            if t < 0.4:
                bob = -40 * (t / 0.4)
            elif t < 0.7:
                bob = -40 + 20 * ((t - 0.4) / 0.3)
            else:
                bob = -20 * (1 - (t - 0.7) / 0.3)
        cr.translate(0, bob)
        self._handles[self.state].render_cairo(cr)
        cr.restore()
        return False
