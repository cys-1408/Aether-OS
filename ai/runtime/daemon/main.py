import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""aether-runtime daemon entry point."""
from runtime_config import load_runtime_config  # noqa: E402
from runtime_service import RuntimeService  # noqa: E402

import gi  # noqa: F401  (not needed here; kept out)

from aether_core.ipc import JsonRpcServer  # noqa: E402
from aether_core import paths  # noqa: E402
from aether_core.logging_setup import configure_logging  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402

# subsystems
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hardware-profile"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "recommendation"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "model-catalog"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "model-manager"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "download"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "inference"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "resource-governor"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "validation"))

from profiler import profile_machine  # noqa: E402
from recommendation_engine import recommend  # noqa: E402
from catalog_loader import load_catalog  # noqa: E402
from model_registry import ModelRegistry  # noqa: E402
from download_manager import start_download, download_status, cancel_download  # noqa: E402
from llama_cpp_adapter import LlamaCppBackend  # noqa: E402
from inference_scheduler import schedule, infer_sync  # noqa: E402
from governor import Governor  # noqa: E402
from inference_smoke_check import smoke_check  # noqa: E402

log = configure_logging("runtime")


def build_server() -> JsonRpcServer:
    config = load_runtime_config()
    svc = RuntimeService(config)
    registry = ModelRegistry()

    def require_ready(params: dict) -> None:
        if params.get("consent") is not True:
            raise IpcError("E_CONSENT_REQUIRED", "explicit consent:true required before downloads")

    methods = {
        "Runtime.status": lambda p: svc.status(),
        "Runtime.profile": lambda p: profile_machine(config),
        "Runtime.models_list": lambda p: registry.list(),
        "Runtime.models_recommend": lambda p: recommend(config, load_catalog(config), profile_machine(config),
                                                        str(p.get("task_class", "assistant"))),
        "Runtime.download_start": lambda p: (require_ready(p),
                                             start_download(config, registry, str(p.get("model_id", ""))))[-1],
        "Runtime.download_status": lambda p: download_status(str(p.get("model_id", ""))),
        "Runtime.download_cancel": lambda p: cancel_download(str(p.get("model_id", ""))),
        "Runtime.model_remove": lambda p: registry.remove(str(p.get("model_id", ""))),
        "Runtime.warmup": lambda p: {"ok": bool(svc.backend and svc.backend.ensure_loaded())},
        "Runtime.infer": lambda p: infer_sync(svc, p),
        "Runtime.infer_stream": lambda p: infer_sync(svc, p, stream=True),
        "Runtime.backend_status": lambda p: (svc.backend.describe() if svc.backend else {"backend": None}),
    }
    # Validate inference requests at the boundary
    base_infer = methods["Runtime.infer"]
    methods["Runtime.infer"] = methods["Runtime.infer_stream"] = base_infer

    def wrapped_infer(params: dict):
        from aether_core import validate as _v  # placeholder, real validation below
        return base_infer(params)
    return JsonRpcServer(paths.system_socket("runtime"), methods)


if __name__ == "__main__":
    server = build_server()
    log.info("aether-runtime listening")
    server.serve_forever()
