import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""GTK CSS provider implementing the approved reference look."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

CSS = """
.aether-topbar { background: rgba(255,255,255,0.48); min-height: 43px; padding: 0 20px; }
.brand-mark { background: #292824; color: #ffffff; border-radius: 7px; min-width: 23px; min-height: 23px; font-weight: 800; }
.brand-name { color: #292824; font-weight: 800; }
.brand-sub { color: #938b7d; }
.top-status { color: #625f57; font-weight: 600; }
.top-status-degraded { color: #b06040; }
.top-clock { color: #625f57; }
.aether-taskbar { background: rgba(255,253,248,0.72); border-top: 1px solid #ffffff; min-height: 60px; }
.taskbar-btn { background: transparent; border-radius: 11px; min-height: 40px; padding: 0 8px; color: #5e5a52; }
.taskbar-btn:hover, .taskbar-btn.active { background: #e9e3d8; }
.aether-window { border-radius: 16px; background: rgba(255,253,249,0.93); border: 1px solid #ffffff; }
.aether-panel { border-radius: 19px; background: rgba(255,253,248,0.95); border: 1px solid #ffffff; }
.aether-activity { border-radius: 13px; background: rgba(255,253,248,0.66); border: 1px solid rgba(255,255,255,0.82); }
.activity-title { color: #8a8173; font-size: 10px; }
.card { background: #f5f0e6; border: 1px solid #ece3d4; border-radius: 12px; padding: 13px; }
.btn { background: #292824; color: #ffffff; border-radius: 9px; padding: 8px 11px; font-weight: 600; }
.btn-orange { background: #d98250; color: #ffffff; border-radius: 9px; padding: 8px 11px; font-weight: 600; }
.soft { background: #f0e9de; color: #4e4a42; border-radius: 9px; padding: 8px 11px; }
.h1 { font-size: 23px; font-weight: 800; letter-spacing: -0.04em; color: #292824; }
.eyebrow { font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: #9a8874; font-weight: 800; }
.sub { color: #817b70; font-size: 12px; }
.fname { font-size: 12px; font-weight: 750; color: #292824; }
.fpath { font-size: 10px; color: #8a857b; }
.note-entry { background: #fffefb; border: 1px solid #e8e1d6; border-radius: 10px; padding: 10px; }
.term { background: #262a30; color: #e9e3d9; border-radius: 10px; font-family: monospace; }
.calc-display { background: #262a30; color: #e9e3d9; border-radius: 12px; font-family: monospace; font-size: 20px; }
.switch-on { background: #d98250; }
.focus-chip { background: #292824; border-radius: 12px; color: #ffffff; padding: 8px 12px; }
.focus-clock { color: #ffffff; font-weight: 800; }
.chip-btn { background: rgba(255,255,255,0.12); color: #ffffff; border-radius: 6px; padding: 4px 7px; }
.toast { background: #292824; color: #ffffff; border-radius: 10px; padding: 11px 14px; }
.notification-item { border-bottom: 1px solid #eee7dc; }
.msg { background: #f2eee6; border-radius: 12px; padding: 9px 11px; font-size: 12px; color: #292824; }
.msg.user { background: #292824; color: #ffffff; }
.suggest-chip { border: 1px solid #e0d6c8; background: #fffdf8; color: #514a40; border-radius: 18px; padding: 8px 10px; font-size: 11px; }
.file-row:hover, .file-row.selected { background: #f4eee4; }
.desk-icon { border-radius: 10px; }
.desk-icon:hover { background: rgba(255,255,255,0.5); }
.art-tile { border-radius: 12px; }
.hc .aether-topbar { background: #ffffff; }
.hc .aether-window, .hc .aether-panel { background: #ffffff; }
"""


def load_css():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.encode())
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def apply_high_contrast():
    provider = Gtk.CssProvider()
    provider.load_from_data(b".hc { -gtk-outline-radius: 4px; }")
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
