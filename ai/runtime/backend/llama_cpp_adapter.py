"""llama.cpp (llama-server) adapter: loopback-only, health-polled, truthful states."""
from __future__ import annotations

import json
import socket
import subprocess
import time
import urllib.request

from backend_interface import Backend
from backend_registry import discover
from gpu_backend_adapter import spawn_options_with_offload


class LlamaCppBackend(Backend):
    def __init__(self):
        self.proc: subprocess.Popen | None = None
        self.port: int | None = None
        self.model_path: str | None = None
        self.crashed = False

    def _find_binary(self) -> str:
        found = discover()
        if not found:
            raise RuntimeError("llama-server not installed (optional backend package)")
        return found[0]

    def start(self, model_path: str, ctx: int, options: dict) -> None:
        self.stop()
        binary = self._find_binary()
        self.port = _free_port()
        gpu_ok = bool(options.get("gpu_ok"))
        argv = [binary] + spawn_options_with_offload(binary, model_path, ctx, self.port, gpu_ok)
        self.proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.model_path = model_path
        deadline = time.time() + 60
        while time.time() < deadline:
            if self.proc.poll() is not None:
                self.crashed = True
                raise RuntimeError(f"llama-server exited with code {self.proc.returncode}")
            if self.health().get("ready"):
                return
            time.sleep(0.5)
        self.stop()
        raise RuntimeError("llama-server did not become healthy within 60s")

    def health(self) -> dict:
        if not self.proc or self.proc.poll() is not None:
            return {"ready": False, "reason": "backend not running"}
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=3) as resp:
                return {"ready": resp.status == 200}
        except (urllib.error.URLError, socket.timeout, ConnectionError, OSError):
            return {"ready": False, "reason": "health endpoint unreachable"}

    def infer(self, request: dict) -> dict:
        payload = json.dumps({
            "prompt": request["prompt"],
            "n_predict": int(request.get("max_tokens", 256)),
            "temperature": float(request.get("temperature", 0.7)),
            "stream": False,
            "stop": request.get("stop") or [],
        }).encode()
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/completion",
                                     data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=request.get("timeout_s", 60)) as resp:
            data = json.loads(resp.read())
        return {"text": data.get("content", ""),
                "tokens_in": data.get("timings", {}).get("prompt_n", 0),
                "tokens_out": data.get("timings", {}).get("predicted_n", 0),
                "latency_ms": int(data.get("timings", {}).get("predicted_ms", 0) +
                                  data.get("timings", {}).get("prompt_ms", 0))}

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = None

    def ensure_loaded(self) -> bool:
        return bool(self.proc and self.health().get("ready"))

    def describe(self) -> dict:
        state = "running" if (self.proc and self.proc.poll() is None) else "stopped"
        return {"backend": "llama.cpp (llama-server)", "state": state,
                "model": self.model_path, "port": self.port,
                "bind": "127.0.0.1 (loopback only)", "crashed": self.crashed}


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
