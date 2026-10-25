import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-reminders — user-scoped persistent reminders."""
from service_main import SystemService  # noqa: E402
import reminder_service as rs  # noqa: E402


def build_service() -> SystemService:
    return SystemService("reminders", "reminders", {
        "Reminders.add": lambda p: rs.add(str(p.get("title", "")), str(p.get("due_iso", ""))),
        "Reminders.list": lambda p: rs.list_reminders(),
        "Reminders.remove": lambda p: rs.remove(int(p.get("id", 0))),
    })


if __name__ == "__main__":
    rs.ReminderFire("/run/aether/notifications.sock").start()
    build_service().run()
