"""TUI menu (the session loop lives in recovery-entry)."""
from recovery_session import RecoverySession  # type: ignore


def run() -> int:
    return RecoverySession().run()
