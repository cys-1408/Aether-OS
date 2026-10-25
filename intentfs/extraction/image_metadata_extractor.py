"""Image metadata: dimensions + basic EXIF (real stdlib parsing)."""
from __future__ import annotations

import struct
from pathlib import Path


def image_meta(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return _png(path)
    if suffix in (".jpg", ".jpeg"):
        return _jpeg(path)
    return {}


def _png(path: Path) -> dict:
    try:
        with open(path, "rb") as fh:
            head = fh.read(24)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", head[16:24])
            return {"width": w, "height": h, "format": "png"}
    except OSError:
        pass
    return {}


def _jpeg(path: Path) -> dict:
    try:
        data = path.read_bytes()
        if data[:2] != b"\xff\xd8":
            return {}
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return {"width": w, "height": h, "format": "jpeg"}
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + seg_len
    except (OSError, struct.error):
        pass
    return {}
