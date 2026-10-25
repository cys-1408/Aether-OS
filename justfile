# AetherOS just recipes (mirror of the Makefile)
set shell := ["bash", "-cu"]

default:
    @just --list

check:
    build/scripts/98-verify-tree.sh

fetch-sources:
    build/scripts/10-fetch-sources.sh

build-kernel: fetch-sources
    build/scripts/20-build-kernel.sh

build-packages:
    build/scripts/30-build-packages.sh

assemble-rootfs: build-packages
    build/scripts/40-assemble-rootfs.sh

iso: check build-installer
    build/scripts/90-create-iso.sh

iso-full:
    build/scripts/90-create-iso.sh
    build/scripts/95-generate-checksums.sh
    build/scripts/99-create-release-manifest.sh

clean:
    rm -rf artifacts build/rootfs.staging build/iso.staging
