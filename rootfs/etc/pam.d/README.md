PAM stack: login/greetd use the distro default system-auth; password changes go
through passwd (PAM) and the account helper for first-boot user creation. No
custom PAM modules are invented in 1.0.0; see docs/security/secrets-management.md.
