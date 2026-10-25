"""Result helpers."""
from __future__ import annotations


def is_ok(result: dict) -> bool:
    return result.get("outcome") == "ok"


def error_message(result: dict) -> str:
    err = result.get("error") or {}
    return err.get("message", "unknown error")
