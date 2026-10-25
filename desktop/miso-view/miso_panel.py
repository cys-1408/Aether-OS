import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Miso assistant panel: real agent connection, suggestions, honest states."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

AGENT_SOCK = "/run/user/{uid}/aether/agent.sock"

SUGGESTIONS = ["What can you do", "Find a file", "Help me focus for 25 minutes",
               "Hide distractions", "Take a five-minute break with me",
               "Organize my desktop", "Open the terminal"]


class MisoPanel(Gtk.Window):
    def __init__(self, shell):
        super().__init__(title="Miso", type=Gtk.WindowType.TOPLEVEL)
        self.shell = shell
        self.set_default_size(340, 420)
        self.set_decorated(False)
        self.get_style_context().add_class("aether-panel")
        self.set_keep_above(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=9, border_width=13)
        avatar = Gtk.Label(label="🐾")
        name_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        name = Gtk.Label(label="Miso", xalign=0)
        name.get_style_context().add_class("fname")
        tag = Gtk.Label(label="Small paws, helpful plans.", xalign=0)
        tag.get_style_context().add_class("sub")
        name_box.pack_start(name, False, False, 0)
        name_box.pack_start(tag, False, False, 0)
        self.status_chip = Gtk.Label(label="IDLE")
        self.status_chip.get_style_context().add_class("sub")
        close_btn = Gtk.Button(label="×")
        close_btn.get_style_context().add_class("soft")
        close_btn.connect("clicked", lambda _: self.hide())
        head.pack_start(avatar, False, False, 0)
        head.pack_start(name_box, False, False, 0)
        head.pack_end(close_btn, False, False, 0)
        head.pack_end(self.status_chip, False, False, 6)
        box.pack_start(head, False, False, 0)

        self.messages = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=13)
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_min_content_height(120)
        scroll.add(self.messages)
        box.pack_start(scroll, True, True, 0)

        self.add_message("Hi — I'm Miso. Tell me what you'd like help with.", who="miso")
        suggest = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, border_width=13)
        self.suggest_box = Gtk.FlowBox()
        self.suggest_box.set_max_children_per_line(2)
        self.suggest_box.set_selection_mode(Gtk.SelectionMode.NONE)
        for s in SUGGESTIONS:
            b = Gtk.Button(label=s)
            b.get_style_context().add_class("suggest-chip")
            b.connect("clicked", self._suggest, s)
            self.suggest_box.add(b)
        suggest.add(self.suggest_box)
        box.pack_start(suggest, False, False, 0)

        form = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, border_width=11)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Tell Miso what you need…")
        self.entry.connect("activate", self._send)
        send_btn = Gtk.Button(label="➤")
        send_btn.get_style_context().add_class("btn")
        send_btn.connect("clicked", self._send)
        self.mic_btn = Gtk.Button(label="🎙")
        self.mic_btn.get_style_context().add_class("soft")
        self.mic_btn.set_sensitive(False)
        self.mic_btn.set_tooltip_text("Voice input needs mic consent + a speech backend (Settings)")
        form.pack_start(self.entry, True, True, 0)
        form.pack_start(self.mic_btn, False, False, 0)
        form.pack_start(send_btn, False, False, 0)
        box.pack_start(form, False, False, 0)
        self.add(box)
        self.hide()

    def toggle(self):
        if self.get_visible():
            self.hide()
        else:
            self.show_all()
            self.entry.grab_focus()

    def _suggest(self, btn, text):
        self.entry.set_text(text)
        self._send(None)

    def _send(self, _btn):
        import threading
        text = self.entry.get_text().strip()
        if not text:
            return
        self.entry.set_text("")
        self.add_message(text, who="user")
        self.status_chip.set_text("THINKING")
        self.add_message("…", who="miso", placeholder=True)

        def work():
            from aether_core.ipc import call
            from aether_core.errors import IpcError
            from aether_core import paths
            try:
                result = call(paths.user_socket("agent"), "Agent.submit", {"text": text}, timeout=120)
                reply = result.get("reply", str(result))
                state = result.get("state", "idle")
            except IpcError as e:
                reply = f"I couldn't reach my action service ({e.message}). The desktop still works — try again shortly."
                state = "degraded"
            GLib.idle_add(self._reply, reply, state)
        threading.Thread(target=work, daemon=True).start()

    def _reply(self, text, state):
        self.status_chip.set_text(state.upper())
        # drop placeholder
        kids = self.messages.get_children()
        if kids and getattr(kids[-1], "_placeholder", False):
            kids[-1].destroy()
        self.add_message(text, who="miso")
        return False

    def add_message(self, text, who="miso", placeholder=False):
        bubble = Gtk.Label(label=text, xalign=0)
        bubble.set_line_wrap(True)
        bubble.set_max_width_chars(38)
        bubble.get_style_context().add_class("msg" + (" user" if who == "user" else ""))
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        if who == "user":
            row.pack_end(bubble, False, False, 0)
        else:
            row.pack_start(bubble, False, False, 0)
        row._placeholder = placeholder
        bubble._placeholder = placeholder
        self.messages.pack_start(row, False, False, 0)
        self.messages.show_all()
