# Boot

grub/ holds the menu template, per-entry configs and theme; initramfs/ holds
the early-userspace init, per-topic configs and numbered hooks; kernel-cmdline/
defines parameter profiles; firmware-policy records redistributable firmware.
The ISO build (build/scripts/60+90) consumes all of these.
