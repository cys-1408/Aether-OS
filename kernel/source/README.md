# kernel/source/README.md
#
# `kernel/source/linux/` is NOT part of the repository.
#
# This directory is populated by the build pipeline:
#
#   kernel/scripts/fetch-upstream.sh
#     downloads the pinned tarball recorded in kernel/upstream.lock
#     (linux-6.12.30.tar.xz), verifies its PGP signature, records the sha256
#     into the lock file, and unpacks the tree here.
#
#   kernel/scripts/apply-patches.sh
#     applies kernel/patches/series on top (empty in 1.0.0).
#
# The directory is gitignored; a clean checkout contains only this README.
# Never commit fetched kernel sources, and never edit files under linux/ —
# the kernel is consumed exactly as upstream (ADR-0001).
