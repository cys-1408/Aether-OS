#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$REPO_ROOT/artifacts/release"
python3 - "$REPO_ROOT" "$OUT" <<'EOF'
import sys, json, hashlib, pathlib, datetime, subprocess
repo, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
artifacts = []
for p in sorted(out.glob("aether-os-*.iso")) + sorted(out.glob("SHA256SUMS")):
    artifacts.append({"name": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "size": p.stat().st_size})
manifest = {
    "schema": "https://aether-os.org/schemas/release-manifest.schema.json",
    "version": (repo / "VERSION").read_text().strip(),
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "kernel": {"lock": "kernel/upstream.lock", "provenance": "kernel/provenance/"},
    "components": ["aether-configs", "aether-services", "aether-desktop", "aether-apps",
                   "aether-ai", "aether-intentfs", "aether-miso", "aether-installer",
                   "aether-recovery", "aether-updater", "linux-aether"],
    "artifacts": artifacts,
    "note": "Boot acceptance gate must pass before publishing (docs/user/installation-guide.md)",
}
(out / "release-manifest.json").write_text(json.dumps(manifest, indent=2))
print("[99] release manifest written")
EOF
