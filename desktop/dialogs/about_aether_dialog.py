import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""About dialog (real version from aether_core)."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

REPO_ROOT = Path(__file__).resolve().parents[3]
import sys
sys.path.insert(0, str(REPO_ROOT / "libraries/libaether-core/python"))
from aether_core.version import VERSION  # noqa: E402


def show_about(parent=None):
    dlg = Gtk.AboutDialog(transient_for=parent, modal=True)
    dlg.set_program_name("Aether")
    dlg.set_version(f"{VERSION} (Aurora)")
    dlg.set_comments("A local-first, AI-native desktop operating system.")
    dlg.set_website("https://aether-os.org")
    dlg.set_license_type(Gtk.License.GPL_3_0)
    dlg.run()
    dlg.destroy()
