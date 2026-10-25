"""Load the backend adapter by name."""
from __future__ import annotations

from backend_registry import discover


def load_backend(preferred: str = "llama-cpp"):
    if preferred == "llama-cpp" and discover():
        from llama_cpp_adapter import LlamaCppBackend
        return LlamaCppBackend()
    return None
