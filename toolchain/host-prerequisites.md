# Host Prerequisites
- x86-64 Linux host (Arch recommended; any distro with the pinned tools works)
- 30 GB free disk (kernel ~6 GB source+build, rootfs ~8 GB, ISO staging ~6 GB, headroom)
- 8 GB RAM (kernel -j builds like more)
- Packages (Arch): base-devel curl cpio zstd xorriso grub python pyyaml rsync squashfs-tools dosfstools e2fsprogs
- Network required only for `make fetch-sources` and package repos at build time; ISO install itself is offline-capable.
