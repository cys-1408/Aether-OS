#!/usr/bin/env bash
# Verify tree integrity: python syntax, shell syntax, JSON/YAML/XML parse, forbidden markers.
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
# Resolve a python interpreter: python3, py (Windows launcher) or python.
PY=""
for cand in python3 py python; do
  # Windows ships App-Store alias stubs named python3/python that are not real
  # interpreters, so verify the candidate actually runs instead of trusting PATH.
  command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'pass' >/dev/null 2>&1 && { PY="$cand"; break; }
done
if [[ -z "$PY" ]]; then
  echo "[98] TREE VERIFICATION FAILED: no python interpreter found"
  exit 1
fi
fail=0
echo "[98] python compileall"
for d in libraries services system desktop applications ai intentfs miso installer recovery package-manager updater security accessibility; do
  [[ -d "$d" ]] || continue
  "$PY" -m compileall -q "$d" 2>/dev/null || fail=1
done
echo "[98] bash -n"
while IFS= read -r f; do bash -n "$f" || { echo "  shell FAIL: $f"; fail=1; }; done < <(rg -l '' --glob '*.sh' kernel boot toolchain build packaging 2>/dev/null)
while IFS= read -r f; do bash -n "$f" || { echo "  initramfs FAIL: $f"; fail=1; }; done < <(rg -l '' boot/initramfs/hooks boot/initramfs/init 2>/dev/null)
echo "[98] json/yaml/xml parse"
"$PY" - <<'EOF' || fail=1
import json, glob, sys
bad = 0
for p in glob.glob('**/*.json', recursive=True):
    if '/artifacts/' in p or p.startswith('artifacts'): continue
    try: json.load(open(p))
    except Exception as e: print(f"  JSON FAIL {p}: {e}"); bad = 1
sys.exit(bad)
EOF
"$PY" - <<'EOF' || fail=1
import yaml, glob, sys
bad = 0
for p in glob.glob('**/*.yaml', recursive=True) + glob.glob('**/*.yml', recursive=True):
    if p.startswith('artifacts'): continue
    try: yaml.safe_load(open(p))
    except Exception as e: print(f"  YAML FAIL {p}: {e}"); bad = 1
sys.exit(bad)
EOF
"$PY" - <<'EOF' || fail=1
import xml.dom.minidom, glob, sys
bad = 0
for pat in ('protocols/dbus/*.xml', '**/*.svg', 'security/**/*.policy', '**/*.gschema.xml'):
    for p in glob.glob(pat, recursive=True):
        try: xml.dom.minidom.parse(p)
        except Exception as e: print(f"  XML FAIL {p}: {e}"); bad = 1
sys.exit(bad)
EOF
echo "[98] forbidden markers"
# Marker scan: policy docs + scanner + mkdtemp templates are legitimate
if rg -n "TODO|FIXME|XXX|NotImplementedError" \
     --glob '!documents/**' \
     --glob '!artifacts/**' --glob '!kernel/source/**' \
     --glob '!CONTRIBUTING.md' --glob '!CONVENTIONS.md' \
     --glob '!build/scripts/98-verify-tree.sh' \
     --glob '!**/tests/**' \
     . >/dev/null 2>&1; then
  rg -n "TODO|FIXME|XXX|NotImplementedError" \
     --glob '!documents/**' \
     --glob '!artifacts/**' --glob '!kernel/source/**' \
     --glob '!CONTRIBUTING.md' --glob '!CONVENTIONS.md' \
     --glob '!build/scripts/98-verify-tree.sh' \
     --glob '!**/tests/**' \
     . | head -20
  fail=1
fi
(( fail == 0 )) && echo "[98] TREE VERIFICATION OK" || echo "[98] TREE VERIFICATION FAILED"
exit $fail
