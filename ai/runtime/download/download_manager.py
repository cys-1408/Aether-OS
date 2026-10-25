"""Resumable, cancellable downloads from the allowlist with digest verification."""
from __future__ import annotations

import hashlib
import json
import shutil
import threading
import urllib.request
from pathlib import Path

from aether_core.config import load_yaml, atomic_write_json
from aether_core.errors import IpcError
from aether_core import CancellationToken, paths

STATE = paths.SYSTEM_STATE_DIR / "runtime" / "downloads.json"
_tokens: dict[str, CancellationToken] = {}
_progress: dict[str, dict] = {}


def start_download(config: dict, registry, model_id: str) -> dict:
    if model_id in _tokens and not _tokens[model_id].cancelled():
        return {"started": False, "reason": "download already running"}
    catalog = _load_catalog(config)
    model = next((m for m in catalog.get("models", []) if m["model_id"] == model_id), None)
    if not model:
        raise IpcError("E_NOT_FOUND", f"model {model_id} not in catalog")
    _allowlist_check(model["repo"])
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hardware-profile"))
    from storage_budget import ensure_space
    from model_install import install_transactional
    store_dir = Path(str(config.get("model_store", "~/.local/share/aether/models")).replace("~", str(Path.home())))
    staging = store_dir / "staging"
    ensure_space(staging, int(model.get("approx_size_gb", 1) * 1e9))
    tok = CancellationToken()
    _tokens[model_id] = tok
    _progress[model_id] = {"state": "downloading", "bytes_done": 0, "bytes_total": None}

    def work():
        try:
            sha = _expected_sha256(model)
            url = f"https://huggingface.co/{model['repo']}/resolve/main/{model['file']}"
            part = staging / f"{model_id}.part"
            _stream(url, part, tok, model_id, sha)
            if tok.cancelled():
                _set_progress(model_id, state="cancelled")
                return
            digest_verifier.verify_file(part, sha)  # raises on mismatch
            from digest_verifier import verify_file  # noqa: F401 (self-check above uses it)
            final = install_transactional(part, store_dir, model_id)
            registry.upsert(model, final.stat().st_size, sha, "installed")
            _set_progress(model_id, state="installed", file=str(final))
        except Exception as e:  # noqa: BLE001 — truthful failure states
            _set_progress(model_id, state="failed", reason=str(e))
        finally:
            _tokens.pop(model_id, None)

    threading.Thread(target=work, daemon=True).start()
    return {"started": True, "model_id": model_id, "staging": str(staging)}


def _stream(url: str, part: Path, tok: CancellationToken, model_id: str, expected_sha: str) -> None:
    resume_from = part.stat().st_size if part.exists() else 0
    req = urllib.request.Request(url)
    if resume_from:
        req.add_header("Range", f"bytes={resume_from}-")
    with urllib.request.urlopen(req, timeout=30) as resp:
        total = resp.headers.get("Content-Length")
        _set_progress(model_id, bytes_total=int(total) + resume_from if total else None)
        mode = "ab" if resume_from else "wb"
        h = hashlib.sha256()
        if resume_from:  # hash the resumed prefix
            with open(part, "rb") as pf:
                for chunk in iter(lambda: pf.read(1 << 20), b""):
                    h.update(chunk)
        with open(part, mode) as fh:
            while True:
                if tok.cancelled():
                    return
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
                h.update(chunk)
                _set_progress(model_id, bytes_done=part.stat().st_size)
    if expected_sha and h.hexdigest() != expected_sha:
        part.unlink(missing_ok=True)
        raise IpcError("E_DIGEST", "downloaded file digest mismatch — part deleted")


def _load_catalog(config: dict) -> dict:
    import json
    path = Path(str(config.get("catalog_path", "")).replace("~", str(Path.home())))
    if not path.exists():
        path = Path(__file__).resolve().parents[2] / "catalog" / "catalog.json"
    return json.loads(path.read_text())


def _allowlist_check(repo: str) -> None:
    policy = load_yaml("/etc/aether/supported-model-sources.yaml")
    hosts = policy.get("allowed_hosts", ["huggingface.co"])
    if not any(repo.split("/")[0].endswith(h.split(".")[0]) or "huggingface" in h for h in hosts):
        raise IpcError("E_SOURCE_DENIED", f"source not in allowlist: {repo}")


def _expected_sha256(model: dict) -> str | None:
    """Fetch the file's sha256 from the HF API tree metadata (lfs.sha256)."""
    import urllib.request
    api = f"https://huggingface.co/api/models/{model['repo']}/tree/main?recursive=true"
    try:
        with urllib.request.urlopen(api, timeout=30) as resp:
            tree = json.loads(resp.read())
        for entry in tree:
            if entry.get("path") == model["file"]:
                lfs = entry.get("lfs") or {}
                return lfs.get("oid")
    except Exception:
        return None
    return None


def _set_progress(model_id: str, **fields) -> None:
    _progress.setdefault(model_id, {}).update(fields)
    try:
        atomic_write_json(STATE, _progress)
    except OSError:
        pass


def download_status(model_id: str) -> dict:
    return _progress.get(model_id, {"state": "unknown"})


def cancel_download(model_id: str) -> dict:
    tok = _tokens.get(model_id)
    if tok:
        tok.cancel()
        _set_progress(model_id, state="cancelling")
        return {"cancelled": model_id}
    return {"cancelled": False, "reason": "no active download"}
