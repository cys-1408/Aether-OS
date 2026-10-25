Privileged Aether actions are declared in security/authorization/polkit/*.policy
and installed to /usr/share/polkit-1/actions/. Helpers run via pkexec with
strict argv validation (docs/architecture/privilege-boundaries.md).
