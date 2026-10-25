#!/usr/bin/env bash
# Check declared build inputs/environment before a release build.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
fail=0
[[ -f "$REPO_ROOT/artifacts/kernel-source/linux-"*".tar.xz" ]] || { echo "kernel source tarball missing"; fail=1; }
[[ -f "$REPO_ROOT/kernel/upstream.lock" ]] || { echo "upstream.lock missing"; fail=1; }
grep -q "^sha256 = UNFILLED" "$REPO_ROOT/kernel/upstream.lock" && { echo "upstream sha256 unfilled"; fail=1; }
[[ -f "$REPO_ROOT/build/reproducibility/environment.lock" ]] || { echo "environment.lock missing"; fail=1; }
exit $fail
