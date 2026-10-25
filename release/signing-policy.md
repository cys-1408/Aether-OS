# Signing Policy
- Release artifacts (ISO, checksums, manifest) carry detached ASCII GPG signatures made by the Aether release signing subkey; the primary key is kept OFFLINE.
- The pacman repository database and packages are signed with the repo subkey registered in pacman-key on install media and installed systems.
- Model catalog digests and update metadata are covered by the same manifest/signature chain.
- Private keys never enter this repository; release/signatures/ holds only public signatures. Rotation: security/cryptography/key-rotation-policy.md.
