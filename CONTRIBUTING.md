# Contributing to AetherOS

## Ground rules
1. Read docs/architecture/system-overview.md and CONVENTIONS.md first. The architecture boundaries (kernel vs user space, capability broker as the only privileged route from the agent) are not negotiable without an ADR.
2. No TODO/FIXME/placeholder code is accepted into the tree. CI runs build/scripts/98-verify-tree.sh, which greps for these markers and fails.
3. Every service change must keep the JSON-RPC namespaces in CONVENTIONS.md stable or bump the documented API version (docs/interfaces/api-versioning.md).
4. Kernel patches require the template in kernel/patches/README.md: rationale, upstream status, threat review, removal path.

## Workflow
- `make check` must pass before every push (syntax, config parsing, forbidden-marker scan).
- Sign-offs: use `git commit -s`. Licensing: SPDX headers for new files, see .reuse/dep5.
- Commits: one logical change, imperative subject (`runtime: bound kv cache to budget`).
