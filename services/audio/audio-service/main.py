import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-audio-service — device selection, volume, mic permission."""
from service_main import SystemService  # noqa: E402
import audio_service, per_app_audio, microphone_permission  # noqa: E402


def build_service() -> SystemService:
    return SystemService("audio", "audio", {
        "Audio.status": lambda p: {"backend": audio_service.backend(), "devices": audio_service.devices(),
                                   "mic": microphone_permission.capture_state()},
        "Audio.devices": lambda p: audio_service.devices(),
        "Audio.set_volume": lambda p: audio_service.set_volume(str(p.get("target", "sink")), int(p.get("percent", 50))),
        "Audio.set_default_sink": lambda p: audio_service.set_default("sink", int(p.get("node_id", 0))),
        "Audio.set_default_source": lambda p: audio_service.set_default("source", int(p.get("node_id", 0))),
        "Audio.streams": lambda p: per_app_audio.streams(),
        "Audio.set_stream_volume": lambda p: per_app_audio.set_stream_volume(int(p.get("id", 0)), int(p.get("percent", 50))),
        "Audio.set_mic_muted": lambda p: microphone_permission.set_mic_muted(bool(p.get("muted", True))),
        "Audio.mic_state": lambda p: microphone_permission.capture_state(),
    })


if __name__ == "__main__":
    build_service().run()
