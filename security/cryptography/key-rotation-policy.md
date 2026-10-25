# Key Rotation
Release signing: rotate the signing SUBKEY annually or on suspicion; primary
key stays offline and signs the new subkey. Repo keys: publish the new key in
a release signed by the old key, ship via update before switching SigLevel
trust. Model catalog digest key: same chain. Compromise procedure: revoke via
keyserver, publish advisory, force re-verification of all signed artifacts.
