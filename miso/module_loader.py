"""Importer for Miso directories whose names are not valid Python identifiers.

The mandated repository layout places Python modules under
``miso/capability-os/`` and ``miso/runtime-client/``; hyphens make those names
unimportable with the ordinary ``import`` statement. This loader imports such
modules by file path with a process-wide cache so repeated loads are cheap and
return the same module object.
"""

from __future__ import annotations

import importlib.util
import sys
import threading
from pathlib import Path
from types import ModuleType

from miso import REPO_ROOT

_LOCK = threading.Lock()
_CACHE: dict[str, ModuleType] = {}


def module_path(relative: str) -> Path:
    """Absolute path of a repo-relative module file."""
    return REPO_ROOT / relative


def load_module(relative: str) -> ModuleType:
    """Import ``miso/<relative>`` by file path (cached)."""
    key = relative.replace("\\", "/")
    with _LOCK:
        cached = _CACHE.get(key)
        if cached is not None:
            return cached
        path = module_path(key)
        if not path.is_file():
            raise ImportError(f"Miso module not found: {key}")
        modname = "miso_ext." + key.removesuffix(".py").replace("/", ".")
        spec = importlib.util.spec_from_file_location(modname, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create import spec for {key}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[modname] = module
        spec.loader.exec_module(module)
        _CACHE[key] = module
        return module


def load_attr(relative: str, attr: str):
    """Load a module by repo-relative path and return one of its attributes."""
    return getattr(load_module(relative), attr)
