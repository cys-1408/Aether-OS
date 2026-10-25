import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-voice-input — opt-in capture + optional local transcription."""
from service_main import SystemService  # noqa: E402
import voice_input, speech_backend_adapter, microphone_state  # noqa: E402


def build_service() -> SystemService:
    return SystemService("voice", "voice", {
        "Voice.status": lambda p: microphone_state.indicator_state(),
        "Voice.start_capture": lambda p: voice_input.record(int(p.get("seconds", 5))),
        "Voice.stop_capture": lambda p: {"note": "capture is duration-bounded; last file reported"},
        "Voice.last_capture": lambda p: voice_input.last_capture(),
        "Voice.transcribe": lambda p: speech_backend_adapter.transcribe(str(p.get("file", ""))),
    })


if __name__ == "__main__":
    build_service().run()
