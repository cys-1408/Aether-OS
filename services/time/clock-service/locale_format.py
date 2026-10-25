"""Locale-aware date/time formatting using the system locale."""
from __future__ import annotations

import locale
from datetime import datetime


def system_locale() -> str:
    try:
        return locale.getlocale()[0] or "C"
    except Exception:
        return "C"


def format_datetime(dt: datetime | None = None, *, with_seconds: bool = True) -> str:
    value = dt or datetime.now()
    fmt = "%c" if with_seconds else "%x %H:%M"
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass
    return value.strftime(fmt)
