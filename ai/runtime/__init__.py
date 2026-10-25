"""Aether Runtime package.

Some runtime sub-packages use hyphenated directory names (hardware-profile,
model-catalog, model-manager, resource-governor). Hyphens are not valid in
Python import statements, so those directories are registered here as proper
packages under underscore aliases, keeping the on-disk layout fixed while
remaining fully importable:

    hardware-profile   -> rt_hardware_profile
    model-catalog      -> rt_model_catalog
    model-manager      -> rt_model_manager
    resource-governor  -> rt_resource_governor
"""
from __future__ import annotations

import importlib.util as _ilu
import sys as _sys
from pathlib import Path as _Path

_HYPHEN_PACKAGES = {
    "hardware-profile": "rt_hardware_profile",
    "model-catalog": "rt_model_catalog",
    "model-manager": "rt_model_manager",
    "resource-governor": "rt_resource_governor",
}


def _register_hyphen_packages() -> None:
    here = _Path(__file__).resolve().parent
    for dirname, modname in _HYPHEN_PACKAGES.items():
        if modname in _sys.modules:
            continue
        pkg_dir = here / dirname
        init_file = pkg_dir / "__init__.py"
        if not init_file.is_file():
            continue
        spec = _ilu.spec_from_file_location(
            modname, init_file, submodule_search_locations=[str(pkg_dir)]
        )
        module = _ilu.module_from_spec(spec)
        _sys.modules[modname] = module
        spec.loader.exec_module(module)


_register_hyphen_packages()
