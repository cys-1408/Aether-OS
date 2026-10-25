# Redistribution Notes
Firmware shipped in the ISO must permit redistribution. The linux-firmware
package carries per-file licenses (WHENCE); the release SBOM records the
package version. Devices requiring non-redistributable firmware are reported
at runtime by the hardware probes ("missing firmware guidance" fallback) and
documented in docs/hardware/known-limitations.md — Aether never silently
claims support it does not deliver.
