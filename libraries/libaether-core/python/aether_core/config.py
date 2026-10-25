"""YAML configuration loading + atomic writes."""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

import yaml

_ENV = re.compile(r"\$\{([A-Z0-9_]+)\}")


def _expand(node: Any) -> Any:
    if isinstance(node, dict):
        return {k: _expand(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_expand(v) for v in node]
    if isinstance(node, str):
        return _ENV.sub(lambda m: os.environ.get(m.group(1), m.group(0)), node)
    return node


def load_yaml(path: Path | str) -> dict:
    """Load a YAML file with ${ENV_VAR} expansion. Empty/missing -> {}."""
    p = Path(path)
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError(f"config root must be a mapping: {p}")
    return _expand(data)


def atomic_write_text(path: Path | str, text: str, *, mode: int = 0o600) -> None:
    """Write text atomically: tmp file in same dir + fsync + os.replace."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=f".{p.name}.", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_write_json(path: Path | str, data: Any, *, mode: int = 0o600) -> None:
    atomic_write_text(path, json.dumps(data, indent=2, sort_keys=True), mode=mode)


def atomic_write_yaml(path: Path | str, data: Any, *, mode: int = 0o600) -> None:
    atomic_write_text(path, yaml.safe_dump(data, sort_keys=False), mode=mode)
