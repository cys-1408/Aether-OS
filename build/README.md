# Build Pipeline
Numbered scripts produce the release: host checks → fetch → kernel → packages
→ rootfs → initramfs → bootloader → live → installer → ISO → checksums →
manifest (plus 98-verify-tree for source integrity). Profiles in profiles/ and
manifests in manifests/ define composition; iso/ defines the image layout;
reproducibility/ records the build environment. Build outputs land in artifacts/
(never committed).
