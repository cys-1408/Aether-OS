# AetherOS Licensing

Aether original code is licensed GPL-3.0-or-later unless a file states otherwise.

## Bundled and inherited licensing obligations
- **Linux kernel** (pinned upstream tree under kernel/source/linux after fetch): GPL-2.0-only WITH Linux-syscall-note. Aether configuration fragments and the (currently empty) patch series are part of this project; the upstream tree keeps its own licenses and MAINTAINERS.
- **Init and base userland**: systemd (LGPL-2.1-or-later), util-linux, coreutils and friends (GPL), assembled from Arch Linux packages by build/scripts/40-assemble-rootfs.sh.
- **Graphical stack**: sway/wlroots (MIT), GTK3/GLib/PyGObject (LGPL-2.1-or-later), gtk-layer-shell (LGPL-3.0-or-later).
- **Tooling**: pacman (GPL-2.0-or-later), mkinitcpio (GPL), grub (GPL-3.0-or-later).
- **Optional inference backend**: llama.cpp (MIT). It is built as a separate package and never linked into Aether services; it is spawned as an external process bound to loopback only.
- **Fonts**: Noto families (OFL-1.1).
- **Model catalog entries** reference external model weights; each catalog entry records its license (for example Apache-2.0, Qwen Research, Llama 3.2 Community). Weights are downloaded only after explicit user consent and are never redistributed by Aether.

## Release obligations
Every release ships LICENSES.md, NOTICE, an SBOM (release/sbom/), source manifests and checksums as described in docs/operations/release-process.md.
