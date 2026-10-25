# Firmware Licensing
Redistributable firmware ships via the linux-firmware package (license metadata: hardware/firmware/license-metadata.yaml, catalog: firmware-catalog.yaml). Non-redistributable blobs are never bundled; where a device needs them, the OS reports missing-firmware guidance (hardware/fallbacks/missing-firmware-guidance.yaml) instead of pretending support.
