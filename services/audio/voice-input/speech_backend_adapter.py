"""Optional local speech backend (whisper.cpp) — honest unavailability."""
from __future__ import annotations

import shutil
import subprocess


def transcribe(wav_path: str) -> dict:
    binary = shutil.which("whisper-cli") or shutil.which("main")
    if not binary:
        return {"supported": False, "reason": "whisper.cpp not installed (optional package)"}
    model = Path("/usr/share/aether/models/whisper/ggml-base.en.bin") if (Path := __import__("pathlib").Path) else None
    if not model or not model.exists():
        return {"supported": False, "reason": "whisper model not installed (Settings → AI Runtime)"}
    try:
        out = subprocess.run([binary, "-m", str(model), "-f", wav_path, "-otxt", "-of", "/tmp/aether-stt"],
                             capture_output=True, text=True, timeout=120)
        text = Path("/tmp/aether-stt.txt").read_text() if Path("/tmp/aether-stt.txt").exists() else ""
        return {"supported": True, "text": text.strip()}
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"supported": False, "reason": str(e)}
