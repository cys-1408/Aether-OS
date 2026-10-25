# Firmware Installation Notice
Firmware loads from /usr/lib/firmware at boot (linux-firmware package).
Devices missing firmware appear in hardware probes with explicit
"missing firmware" reasons and docs/hardware/known-limitations.md pointers —
Aether never silently pretends unsupported hardware works.
