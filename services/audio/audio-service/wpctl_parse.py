"""wpctl / pactl output parsers shared by the AetherOS audio-service.

PipeWire's ``wpctl status`` is an indented tree, not JSON; the parsers here
track the Audio -> Sinks/Sources/Devices/Streams sections and extract node
ids, names, default markers, volumes and mute flags.  A pactl fallback parser
covers PulseAudio-only installs.
"""
from __future__ import annotations

import re

_ENTRY_RE = re.compile(
    r"^\s*\*?\s*(\d+)\.\s+(?P<name>.+?)(?:\s+\[vol:\s*(?P<vol>[0-9.]+)\])?"
    r"(?P<flags>.*)$")
_MUTED_RE = re.compile(r"\[MUTED[^\]]*\]", re.IGNORECASE)


def _parse_entry(line: str) -> dict | None:
    match = _ENTRY_RE.match(line)
    if not match:
        return None
    name = match.group("name").strip()
    muted = bool(_MUTED_RE.search(match.group("flags") or ""))
    return {
        "id": int(match.group(1)),
        "name": name.rstrip(":").rstrip(),
        "is_stream": match.group("name").endswith(":"),
        "volume": float(match.group("vol")) if match.group("vol") else None,
        "muted": muted,
        "default": line.lstrip().startswith("*"),
    }


def parse_wpctl_status(text: str) -> dict:
    """Parse `wpctl status` into devices/sinks/sources/streams lists."""
    sections: dict[str, list] = {"Devices": [], "Sinks": [], "Sources": [], "Streams": []}
    in_audio = False
    current: str | None = None
    for raw in text.splitlines():
        stripped = raw.strip()
        if re.match(r"^(Audio|Video|Settings|WirePlumber|API|Plugin)[a-zA-Z ]*:$", raw.strip()) \
                or re.match(r"^[A-Z][A-Za-z ]+$", stripped) and not stripped.endswith(":"):
            if stripped == "Audio":
                in_audio = True
                current = None
            elif not raw.startswith((" ", "│", "├", "└")):
                in_audio = False
                current = None
            continue
        if not in_audio:
            continue
        section_m = re.search(r"(Devices|Sinks|Sources|Streams):", stripped)
        if section_m:
            current = section_m.group(1)
            continue
        if current is None:
            continue
        entry = _parse_entry(stripped)
        if entry:
            sections[current].append(entry)
    return sections


def parse_wpctl_get_volume(text: str) -> dict:
    """Parse `wpctl get-volume @DEFAULT_AUDIO_SINK@` -> {'volume','muted'}."""
    text = text.strip()
    muted = "MUTED" in text.upper()
    match = re.search(r"Volume:\s*([0-9.]+)", text)
    return {
        "volume": float(match.group(1)) if match else None,
        "muted": muted,
    }


def parse_pactl_blocks(text: str, kind: str) -> list[dict]:
    """Parse `pactl list sinks|sources|sink-inputs` output blocks."""
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if re.match(rf"^{re.escape(kind)} #\d+", line.strip()):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)

    out: list[dict] = []
    for block in blocks:
        entry: dict = {"id": None, "name": None, "description": None,
                       "muted": None, "volume_percent": None, "app": None}
        for line in block:
            stripped = line.strip()
            id_m = re.match(rf"^{re.escape(kind)} #(\d+)", stripped)
            if id_m:
                entry["id"] = int(id_m.group(1))
                continue
            if stripped.startswith(("Name:", "Description:", "Mute:", "Volume:")):
                key, _, value = stripped.partition(":")
                value = value.strip()
                if key == "Name:":
                    entry["name"] = value
                elif key == "Description:":
                    entry["description"] = value
                elif key == "Mute:":
                    entry["muted"] = value.lower() == "yes"
                elif key == "Volume:":
                    percents = re.findall(r"/\s*(\d+)%", value)
                    if percents:
                        entry["volume_percent"] = int(percents[0])
            elif stripped.startswith("application.name"):
                app_m = re.search(r'=\s*"(.*)"', stripped)
                if app_m:
                    entry["app"] = app_m.group(1)
        out.append(entry)
    return out
