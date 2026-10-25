"""Shared resource-budget structures."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .config import load_yaml


@dataclass
class ResourceBudget:
    """Bounded resource envelope for a service or task."""
    max_mem_mb: int = 512
    cpu_percent: int = 50
    max_concurrent: int = 2
    disk_mb: int = 2048
    source: str = field(default="default")

    @classmethod
    def from_yaml(cls, path: Path | str, section: str) -> "ResourceBudget":
        cfg = load_yaml(path)
        node = cfg.get(section, {}) or {}
        return cls(
            max_mem_mb=int(node.get("max_mem_mb", 512)),
            cpu_percent=int(node.get("cpu_percent", 50)),
            max_concurrent=int(node.get("max_concurrent", 2)),
            disk_mb=int(node.get("disk_mb", 2048)),
            source=str(path),
        )

    def as_dict(self) -> dict:
        return {
            "max_mem_mb": self.max_mem_mb, "cpu_percent": self.cpu_percent,
            "max_concurrent": self.max_concurrent, "disk_mb": self.disk_mb,
        }
