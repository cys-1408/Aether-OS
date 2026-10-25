"""Package bridge for the Aether desktop tree.

Several shell directories are named with hyphens (``window-manager``,
``desktop-icons``, ``miso-view``, ``focus-mode``, ``settings-integration``)
because the deliverable layout mandates them. Python's ``import`` statement
cannot reference such names directly, so this module registers underscore
aliases (e.g. ``window_manager`` -> ``desktop/window-manager``) and makes sure
the shared ``aether_core`` library is importable.

Every shell entry point imports :mod:`shell.pkgmap` first; after that, plain
``import window_manager.window_state`` style imports work everywhere.
"""
from __future__ import annotations

import importlib
import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType

LOG = logging.getLogger("aether.shell.pkgmap")

DESKTOP_DIR = Path(__file__).resolve().parent.parent          # desktop/
REPO_DIR = DESKTOP_DIR.parent                                  # repo root
AETHER_CORE_SRC = REPO_DIR / "libraries" / "libaether-core" / "python"

#: hyphenated directory name -> importable alias
HYPHEN_PACKAGES: dict[str, str] = {
    "window-manager": "window_manager",
    "desktop-icons": "desktop_icons",
    "miso-view": "miso_view",
    "focus-mode": "focus_mode",
    "settings-integration": "settings_integration",
}

bootstrapped = False


def _ensure_sys_path() -> None:
    for path in (str(DESKTOP_DIR), str(AETHER_CORE_SRC)):
        if path not in sys.path:
            sys.path.insert(0, path)


def _register_alias(hyphen_name: str, alias: str) -> ModuleType:
    """Register *alias* as an importable package pointing at the hyphen dir."""
    dir_path = DESKTOP_DIR / hyphen_name
    spec = importlib.util.spec_from_file_location(
        alias, str(dir_path / "__init__.py"),
        submodule_search_locations=str(dir_path),
    )
    if spec is None or spec.loader is None:  # pragma: no cover - structural only
        raise ImportError(f"cannot build spec for {hyphen_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


def bootstrap() -> None:
    """Register aliases for hyphenated packages (idempotent)."""
    global bootstrapped  # noqa: WPS420 - deliberate module-level cache
    if bootstrapped:
        return
    _ensure_sys_path()
    for hyphen_name, alias in HYPHEN_PACKAGES.items():
        if alias in sys.modules:
            continue
        try:
            importlib.import_module(alias)
            continue
        except ImportError:
            pass
        if (DESKTOP_DIR / hyphen_name).is_dir():
            _register_alias(hyphen_name, alias)
    bootstrapped = True


def import_pkg(hyphen_name: str) -> ModuleType:
    """Import a possibly-hyphenated desktop package by its directory name."""
    bootstrap()
    if hyphen_name in HYPHEN_PACKAGES:
        return importlib.import_module(HYPHEN_PACKAGES[hyphen_name])
    return importlib.import_module(hyphen_name)


bootstrap()
