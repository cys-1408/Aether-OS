import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""Runtime.status wrapper."""
from aether_core.ipc import call  # noqa: F401
from aether_core import paths  # noqa: F401
from aether_core.errors import IpcError  # noqa: F401


def infer(prompt: str, task_class: str = "assistant", max_tokens: int = 256,
          timeout: float = 60.0) -> dict:
    try:
        result = call(paths.system_socket("runtime"), "Runtime.infer",
                      {"request_id": f"miso-{int(__import__('time').time()*1000)}",
                        "task_class": task_class, "prompt": prompt,
                        "max_tokens": max_tokens, "timeout_s": int(timeout)},
                      timeout=timeout + 5)
        return result or {"state": "error", "error": {"message": "empty reply"}}
    except IpcError as e:
        return {"state": "unavailable", "error": {"message": e.message}}
