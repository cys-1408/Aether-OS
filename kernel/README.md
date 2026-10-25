# Kernel

Aether uses the pinned upstream Linux tree. `source/linux/` is populated by
`scripts/fetch-upstream.sh` and is never committed. Configuration is assembled
from `configs/aether_defconfig` + `configs/fragments/*` via `scripts/merge-config.sh`;
the (intentionally empty at 1.0.0) patch series is applied by `scripts/apply-patches.sh`.
Build with `scripts/build-kernel.sh`; provenance is collected into `provenance/`.
