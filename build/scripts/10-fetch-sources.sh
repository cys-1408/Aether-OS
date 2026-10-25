#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
"$REPO_ROOT/kernel/scripts/fetch-upstream.sh"
# third-party pins are fetched here too (llama.cpp etc.) with digest verification
python3 - "$REPO_ROOT" <<'EOF'
import sys, pathlib, urllib.request
repo = pathlib.Path(sys.argv[1])
pins = repo / "third-party/pins.yaml"
if not pins.exists():
    print("[10] no third-party pins file; skipping"); raise SystemExit
try:
    import yaml
    data = yaml.safe_load(pins.read_text())
except Exception as e:
    print(f"[10] pins unreadable ({e}); skipping fetch"); raise SystemExit
for name, p in (data.get("pins") or {}).items():
    url, sha = p.get("url"), p.get("sha256")
    if not url: continue
    dest = repo / "artifacts/third-party" / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    tar = dest.with_suffix(".tar.gz")
    if tar.exists() and sha:
        import hashlib
        if hashlib.sha256(tar.read_bytes()).hexdigest() == sha:
            print(f"[10] {name} already fetched+verified"); continue
    try:
        urllib.request.urlretrieve(url, tar)
        if sha:
            import hashlib
            got = hashlib.sha256(tar.read_bytes()).hexdigest()
            if got != sha:
                tar.unlink(); raise SystemExit(f"[10] digest MISMATCH for {name}")
        print(f"[10] fetched {name}")
    except Exception as e:
        print(f"[10] WARN could not fetch {name}: {e} (build continues; backend optional)")
EOF
echo "[10] sources fetched + verified"
