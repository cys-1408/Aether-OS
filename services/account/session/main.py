"""aether-session coordinator (system-level view of sessions)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))

from service_main import SystemService  # noqa: E402
import session_manager, login_flow, logout_flow  # noqa: E402


def build_service() -> SystemService:
    return SystemService("session", "session", {
        "Session.status": lambda p: session_manager.list_sessions(),
        "Session.show": lambda p: session_manager.show_session(str(p.get("session_id", ""))),
        "Session.lock": lambda p: {"action": "swaylock", "policy": "see auth_provider.lock_screen_policy"},
        "Session.logout": lambda p: logout_flow.logout(),
        "Session.config": lambda p: login_flow.installed_config_ok(),
    })


if __name__ == "__main__":
    build_service().run()
