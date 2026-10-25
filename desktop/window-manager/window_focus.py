"""Focus helpers."""
from window_manager import WindowManager  # noqa: F401


def focus_by_app(wm: WindowManager, app_id: str) -> dict:
    for win in wm.windows():
        if win.get("app_id") == app_id:
            return wm.focus_window(win["id"])
    return {"error": f"no window for {app_id}"}
