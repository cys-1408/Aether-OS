#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
"$REPO_ROOT/kernel/scripts/build-kernel.sh"
"$REPO_ROOT/kernel/scripts/collect-provenance.sh"
