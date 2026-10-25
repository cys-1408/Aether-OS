# AetherOS top-level build orchestration. All heavy lifting lives in build/scripts/.
SHELL := /bin/bash
BSCRIPTS := build/scripts
ARTIFACTS := artifacts

.PHONY: help check fetch-sources build-kernel build-packages assemble-rootfs build-initramfs stage-bootloader build-live build-installer iso checksums release-manifest clean

help:
	@echo "AetherOS 1.0.0 build targets:"
	@echo "  make check            - verify tree integrity (syntax, configs, markers)"
	@echo "  make fetch-sources    - fetch + verify pinned upstream sources"
	@echo "  make build-kernel     - build the configured Aether kernel"
	@echo "  make build-packages   - build Aether pacman packages into artifacts/repo"
	@echo "  make assemble-rootfs  - assemble the root filesystem"
	@echo "  make build-initramfs  - build initramfs images"
	@echo "  make stage-bootloader - stage grub + EFI images"
	@echo "  make build-live       - assemble the live environment"
	@echo "  make build-installer  - assemble the installer environment"
	@echo "  make iso              - produce the bootable ISO (runs everything needed)"
	@echo "  make checksums        - sha256 for release artifacts"
	@echo "  make release-manifest - generate release manifest"

check:
	$(BSCRIPTS)/98-verify-tree.sh

fetch-sources:
	$(BSCRIPTS)/10-fetch-sources.sh

build-kernel: fetch-sources
	$(BSCRIPTS)/20-build-kernel.sh

build-packages:
	$(BSCRIPTS)/30-build-packages.sh

assemble-rootfs: build-packages
	$(BSCRIPTS)/40-assemble-rootfs.sh

build-initramfs: assemble-rootfs
	$(BSCRIPTS)/50-build-initramfs.sh

stage-bootloader: build-initramfs
	$(BSCRIPTS)/60-stage-bootloader.sh

build-live: stage-bootloader
	$(BSCRIPTS)/70-build-live-environment.sh

build-installer: build-live
	$(BSCRIPTS)/80-build-installer-image.sh

iso: check build-installer
	$(BSCRIPTS)/90-create-iso.sh

checksums: iso
	$(BSCRIPTS)/95-generate-checksums.sh

release-manifest: checksums
	$(BSCRIPTS)/99-create-release-manifest.sh

clean:
	rm -rf $(ARTIFACTS) build/rootfs.staging build/iso.staging
