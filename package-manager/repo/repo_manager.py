"""Repo building with repo-add (+ gpg signing when a key exists)."""
from __future__ import annotations

import subprocess
from pathlib import Path


def build_repo(repo_dir: str, sign: bool = False) -> dict:
    d = Path(repo_dir)
    pkgs = sorted(d.glob("*.pkg.tar.*"))
    if not pkgs:
        return {"packages": 0}
    argv = ["repo-add"]
    if sign:
        argv.append("--sign")
    argv.append(str(d / "aether.db.tar.gz"))
    argv += [str(p) for p in pkgs]
    out = subprocess.run(argv, capture_output=True, text=True, timeout=600)
    return {"packages": len(pkgs), "ok": out.returncode == 0}
