"""Resume/recover an interrupted install from persisted state."""
from __future__ import annotations

from installer_state import InstallerState  # type: ignore  # app module path


def resume_point() -> str | None:
    state = InstallerState()
    steps = state.data["completed_steps"]
    return steps[-1] if steps else None
