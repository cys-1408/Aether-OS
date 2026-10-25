import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-backup — real manifest backups, verify, restore."""
from service_main import SystemService  # noqa: E402
import backup_service as bs  # noqa: E402
import restore_service as rs  # noqa: E402
from backup_scheduler import schedule_state  # noqa: E402


def build_service() -> SystemService:
    return SystemService("backup", "backup", {
        "Backup.status": lambda p: bs.status(),
        "Backup.targets": lambda p: bs.targets(),
        "Backup.run": lambda p: bs.run_backup(str(p.get("target", "")), p.get("includes")),
        "Backup.verify": lambda p: bs.verify(str(p.get("file", ""))),
        "Backup.restore_preview": lambda p: rs.preview(str(p.get("file", ""))),
        "Backup.restore": lambda p: rs.restore(
            str(p.get("file", "")), conflict_policy=str(p.get("conflict_policy", "fail")),
            confirm_overwrite=bool(p.get("confirm_overwrite", False))),
        "Backup.schedule": lambda p: schedule_state(),
    })


if __name__ == "__main__":
    build_service().run()
