# AetherOS

AetherOS is a real Linux-based desktop operating system distribution built around a
local-first AI plane. It ships an upstream Linux kernel, systemd, a Wayland desktop
(sway + a GTK3/PyGObject shell), an Arch-based userland assembled with pacstrap and
pacman packages, and a strictly user-space AI stack (llama.cpp inference, IntentFS
semantic file index, the Miso agent) that is fully optional and fully local.

## What is in this repository

This is the **source distribution** of AetherOS 1.0.0. It is not a website and not a
binary artifact dump. Top-level layout:

| Directory | Contents |
|---|---|
| `docs/` | Architecture, kernel, boot, AI, security, operations and user documentation |
| `kernel/` | Pinned upstream kernel (6.12.x LTS), defconfig, fragments, build scripts, provenance |
| `boot/` | GRUB configuration, initramfs `init` and hooks, kernel command line, firmware policy |
| `toolchain/` | Build-host toolchain policy, version floors, cross-toolchain definitions |
| `build/` | Numbered build pipeline scripts, profiles, package manifests, reproducibility data |
| `release/` | Release manifest schema, signing policy, SBOM and release output conventions |
| `packaging/` | pacman `PKGBUILD`s for every Aether package, `pacman.conf`, `makepkg.conf` |

Component source trees (`services/`, `desktop/`, `ai/`, `intentfs/`, `miso/`,
`installer/`, `recovery/`, `updater/`, `applications/`, `libraries/`, …) are owned by
their respective implementation agents; see `CONVENTIONS.md` for the binding
engineering contract.

## Supported profile (1.0.0)

* Architecture: **x86_64** (UEFI boot preferred; legacy BIOS boot is documented in
  `docs/boot-and-install/firmware-matrix.md`).
* Storage: ext4 root filesystem (default), optional LUKS2 encryption, optional btrfs/xfs.
* AI: local inference via llama.cpp (`llama-server`) on loopback only. No cloud calls.
  Without models or without compatible hardware the OS remains fully functional.

## Building

The build entry point is:

```sh
make iso        # full pipeline: fetch → kernel → packages → rootfs → ISO
make check      # verify tree integrity (build/scripts/98-verify-tree.sh)
```

All stages delegate to the numbered scripts in `build/scripts/`; the `Makefile` and
`justfile` are thin drivers over them. Build prerequisites (Arch-based host, ≥30 GB
disk) are listed in `toolchain/host-prerequisites.md`.

**Honest statement about artifacts:** ISO images, kernel packages, pacman repositories
and checksums are *produced by the build pipeline at release time* and published on the
release infrastructure. This repository intentionally contains **no prebuilt ISO
artifacts, no kernel tarballs, no model weights and no signing keys**. Everything under
`artifacts/`, `kernel/source/linux/` and `release/checksums|signatures/` is generated
by `build/scripts/` and ignored by git.

## Kernel

The kernel is pinned to **Linux 6.12.30 (6.12 LTS series)**, recorded in
`kernel/upstream.lock` with the tarball URL and a recorded-sha256 mechanism. The hash
slot is filled in by `kernel/scripts/fetch-upstream.sh` at fetch time and verified by
`kernel/scripts/verify-upstream.sh`; a fresh tree fails the verify step honestly rather
than shipping a fabricated hash. Aether ships **zero kernel patches** in 1.0.0
(`kernel/patches/series` is empty by design).

## License

The AetherOS-specific code in this repository is Apache-2.0. The upstream Linux kernel
is GPL-2.0-only; userland components retain their own licenses (GPL/LGPL/MIT/etc.).
See `LICENSES.md` and `NOTICE`.
