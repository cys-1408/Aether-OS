"""Stable backend contract — independent of any single inference engine."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Backend(ABC):
    @abstractmethod
    def start(self, model_path: str, ctx: int, options: dict) -> None: ...
    @abstractmethod
    def health(self) -> dict: ...
    @abstractmethod
    def infer(self, request: dict) -> dict: ...
    @abstractmethod
    def stop(self) -> None: ...
    @abstractmethod
    def describe(self) -> dict: ...
