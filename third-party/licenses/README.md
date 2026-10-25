# third-party/licenses/

Retained license texts and notices for every third-party component that ships
in Aether release media.

Current contents (maintained here rather than in this directory because each
is also embedded with its source):

| Component | License origin | Where the text lives |
| --- | --- | --- |
| Linux kernel | GPL-2.0-only (kernel source) | fetched pinned source (kernel/upstream.lock); COPYING in the tree |
| sway, wlroots | MIT | distribution package — license text from the distro package, recorded in release/source-manifest/ |
| GTK3, GLib | LGPL-2.1-or-later | distro packages |
| python | PSF-2.0 | distro package |
| busybox | GPL-2.0-only | build-time binary + NOTICE in initramfs build |
| cryptsetup | GPL-2.0-or-later (files incl. LUKS) | distro package |
| GRUB | GPL-3.0-or-later | distro package |
| NetworkManager | GPL-2.0-or-later | distro package |
| PipeWire/WirePlumber | MIT/LGPL-2.1-or-later | distro packages |
| Noto fonts | OFL-1.1 | font packages (fonts carry their own license file) |
| NOVA/other redistributable firmware | see hardware/firmware/license-metadata.yaml + firmware/license-metadata.yaml |

Rules:
1. License text for source-tree-embedded components (Aether code) lives in
   LICENSES.md / NOTICE at the repo root (SPDX conventions, .reuse/dep5).
2. For distro packages, a LICENSES capture is generated at release time into
   release/source-manifest/ (build/scripts/99-create-release-manifest.sh).
3. No component enters the release without its license present and recorded
   in the SBOM (release/sbom/).
