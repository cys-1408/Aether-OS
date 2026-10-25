import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-clipboard — policy-gated clipboard service (user scope)."""
from service_main import SystemService  # noqa: E402
import clipboard_service as cs  # noqa: E402


def build_service() -> SystemService:
    return SystemService("clipboard", "clipboard", {
        "Clipboard.status": lambda p: {"history_enabled": cs.enabled()},
        "Clipboard.get": lambda p: cs.get(),
        "Clipboard.set": lambda p: cs.set(str(p.get("text", ""))),
        "Clipboard.history": lambda p: cs.history(),
        "Clipboard.clear": lambda p: cs.clear(),
    })


if __name__ == "__main__":
    build_service().run()
