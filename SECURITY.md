# Security Policy

## Reporting
Email security@aether-os.org (PGP key in docs/security/incident-response.md). Report suspected vulnerabilities privately; do not open public issues for exploitable defects. We aim to acknowledge within 3 business days and to publish fixes with the next point release, coordinated as CVEs when applicable.

## Supported releases
The 1.0.x series receives security fixes. The pinned upstream kernel tracks the 6.12 LTS series; CVE status is recorded in kernel/notes/release-cve-status.md and refreshed at every release (docs/kernel/update-and-cve-process.md).

## Scope notes
Aether's trusted base is the kernel, boot chain, systemd, polkit and the narrowly scoped privileged helpers listed in docs/architecture/privilege-boundaries.md. The Miso agent, the inference backend and file-content processing are unprivileged and treated as untrusted input, as described in docs/security/threat-model.md.
