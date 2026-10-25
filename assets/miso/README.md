# assets/miso — companion artwork

The approved Miso companion artwork (idle/walk/run/jump/sleep/focus/search/carry
states + base SVG) lives in `desktop/assets/miso/` and is consumed directly by
the native shell (`desktop/miso-view/`). This directory is the asset-level
anchor: release tooling copies from `desktop/assets/miso/` when packaging; do
not duplicate the SVGs here to avoid double-maintaining them.

State mapping to the reference design:

| State | File (desktop/assets/miso/) |
| --- | --- |
| idle | miso-idle.svg |
| walk | miso-walk.svg |
| run | miso-run.svg |
| jump | miso-jump.svg |
| sleep | miso-sleep.svg |
| focus | miso-focus.svg |
| search | miso-search.svg |
| carry | miso-carry.svg |
| base | miso.svg |

Animation timing is defined in `desktop/theme/motion.yaml` and honored with
reduced-motion in `accessibility/motion/reduced-motion.yaml`.
