"""Live system status (real service probes + audio mic state)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class SystemStatusWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.cpu_lbl = Gtk.Label(label="cpu –")
        self.mem_lbl = Gtk.Label(label="mem –")
        self.mic_lbl = Gtk.Label(label="mic –")
        for lbl in (self.cpu_lbl, self.mem_lbl, self.mic_lbl):
            lbl.get_style_context().add_class("sub")
            self.pack_start(lbl, False, False, 0)
        self._refresh()
        GLib.timeout_add_seconds(3, self._refresh)

    def _refresh(self):
        import threading

        def probe():
            from aether_core.ipc import call
            from aether_core.errors import IpcError
            from aether_core import paths
            cpu = mem = mic = "?"
            try:
                s = call(paths.system_socket("hardware-probe"), "Hardware.summary", {}, timeout=3)
                mem = f"{(s.get('memory', {}).get('available_mb') or 0)}MB free"
            except IpcError:
                cpu = "unavailable"
            try:
                a = call(paths.system_socket("audio"), "Audio.mic_state", {}, timeout=3)
                mic = "muted" if a.get("muted") else "live"
            except IpcError:
                mic = "n/a"
            GLib.idle_add(self._apply, cpu, mem, mic)
        threading.Thread(target=probe, daemon=True).start()
        return True

    def _apply(self, cpu, mem, mic):
        self.cpu_lbl.set_text(f"cpu {cpu}")
        self.mem_lbl.set_text(f"mem {mem}")
        self.mic_lbl.set_text(f"mic {mic}")
        return False
