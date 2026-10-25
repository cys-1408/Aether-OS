"""Aether Gallery — real image listing, thumbnails, zoom/pan."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
for p in (REPO_ROOT / "libraries/libaether-core/python", REPO_ROOT / "applications/app-framework"):
    sys.path.insert(0, str(p))

from application_context import AetherApp  # noqa: E402

import gi  # noqa: E402
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib  # noqa: E402

FORMATS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"}


class GalleryWindow(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, border_width=12)
        self.app = app
        self.images: list[Path] = []
        self.current: GdkPixbuf.Pixbuf | None = None
        self.zoom = 1.0

        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        pick = Gtk.Button(label="Open folder")
        pick.get_style_context().add_class("btn")
        pick.connect("clicked", self._pick_folder)
        bar.pack_start(pick, False, False, 0)
        self.src_lbl = Gtk.Label(label="choose a folder to browse", xalign=0)
        self.src_lbl.get_style_context().add_class("sub")
        bar.pack_start(self.src_lbl, True, True, 0)
        self.pack_start(bar, False, False, 0)

        self.flow = Gtk.FlowBox()
        self.flow.set_max_children_per_line(4)
        self.flow.set_min_children_per_line(2)
        self.flow.connect("child-activated", self._view_image)
        flow_scroll = Gtk.ScrolledWindow()
        flow_scroll.set_vexpand(True)
        flow_scroll.add(self.flow)
        self.pack_start(flow_scroll, True, True, 0)

        self.viewer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.image = Gtk.Image()
        self.viewer.pack_start(self.image, True, True, 0)
        zoom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for label, factor in (("Zoom in", 1.25), ("Zoom out", 0.8), ("Back", 0)):
            b = Gtk.Button(label=label)
            b.get_style_context().add_class("soft")
            b.connect("clicked", self._zoom, factor)
            zoom_row.pack_start(b, False, False, 0)
        self.viewer.pack_start(zoom_row, False, False, 0)
        self.viewer.hide()
        self.pack_start(self.viewer, True, True, 0)

    def _pick_folder(self, _btn):
        from desktop.dialogs.file_picker_adapter import choose_folder
        folder = choose_folder(self.get_toplevel(), "Choose image folder")
        if folder:
            self.load_folder(Path(folder))

    def load_folder(self, folder: Path):
        self.images = sorted(p for p in folder.iterdir()
                             if p.suffix.lower() in FORMATS and p.is_file())
        self.src_lbl.set_text(f"{folder} — {len(self.images)} images")
        for child in self.flow.get_children():
            self.flow.remove(child)
        for p in self.images[:200]:
            try:
                pix = GdkPixbuf.Pixbuf.new_from_file_at_size(str(p), 160, 160)
                img = Gtk.Image.new_from_pixbuf(pix)
                img.set_tooltip_text(p.name)
                self.flow.add(img)
            except GLib.Error:
                continue
        self.flow.show_all()

    def _view_image(self, flow, child):
        idx = child.get_index()
        if idx < len(self.images):
            p = self.images[idx]
            try:
                self._original = GdkPixbuf.Pixbuf.new_from_file(str(p))
                self._current_path = p
                self.zoom = 1.0
                self._render()
                flow.get_parent().hide()
                self.viewer.show_all()
            except GLib.Error as e:
                self.src_lbl.set_text(f"decode failed: {e.message}")

    def _render(self):
        if not self._original:
            return
        w = int(self._original.get_width() * self.zoom)
        h = int(self._original.get_height() * self.zoom)
        w = max(16, min(w, 4000)); h = max(16, min(h, 4000))
        scaled = self._original.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(scaled)

    def _zoom(self, _btn, factor):
        if factor == 0:
            self.viewer.hide()
            self.flow.get_parent().show_all()
            return
        self.zoom = max(0.1, min(8.0, self.zoom * factor))
        self._render()


class GalleryApp(AetherApp):
    app_id = "org.aether.Apps.Gallery"
    title = "Gallery"

    def build_window(self):
        win = super().build_window()
        win.set_default_size(560, 460)
        win.add(GalleryWindow(self))
        return win


if __name__ == "__main__":
    sys.exit(GalleryApp().run(sys.argv))
