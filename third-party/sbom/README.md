# third-party/sbom/

Generated software bill of materials (SPDX 2.3 JSON) output — **generated, not
hand-maintained**. Produced at release time by
`build/scripts/99-create-release-manifest.sh` into `release/sbom/` and mirrored
here for the dependency inventory view.

Generation inputs:
- `third-party/pins.yaml` + `third-party/source-lock.yaml` (explicit pins)
- pacman package list of the assembled rootfs (build/staging)
- kernel build provenance (`kernel/provenance/`)
- catalog of redistributable firmware (`firmware/firmware-catalog.yaml`)

Do not commit generated SBOM files for an unbuilt release; the empty directory
is protected with this README only.
