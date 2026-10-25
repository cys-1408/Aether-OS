# Trust boundaries

## Trust levels

| Ring | Components | Trust basis |
| --- | --- | --- |
| T0 (trusted base) | firmware, Linux kernel, systemd, pacman, sudo/su, cryptsetup, kernel modules | upstream supply chain + signed release artifacts (`release/signing-policy.md`) |
| T1 (privileged helpers) | `aether-broker`, narrowly scoped polkit helpers (`security/authorization/polkit/*`) | root-tightest-sandboxed units; policy files root-owned 0644 |
| T2 (user-space services) | runtime daemon, intentfs, ledger, workspace, notification, hardware probe | dynamic users + systemd sandbox confs (`security/sandbox/*`) |
| T3 (user applications) | shell, Files, Writer, Terminal, Settings … | session-scope, user-owned config only |
| T4 (agent) | Miso planner + model | unprivileged; **never** self-modifies policy |

## Data crossing boundaries

- **Model output** → never executed as shell; enters only as typed,
  schema-validated capability requests (`miso/safety/no_shell_interpolation.py`).
- **File contents** (extracted text, filenames) → treated as *untrusted data*,
  wrapped by the prompt-injection filter before any model contact
  (`miso/safety/untrusted_content_boundary.py`).
- **IPC** → JSON-RPC over unix sockets with SO_PEERCRED identity checks
  (`miso/peercreds.py`, `libraries/libaether-ipc/src/authentication.c`).
- **Network** → no outbound transfer without a consented capability policy
  (`rootfs/etc/aether/privacy-defaults.yaml`,
  `networking/policies/per_capability_transfer.yaml`).
- **Model artifacts** → digest + manifest verification before load
  (`ai/runtime/validation/model_integrity.py`).

## Invariants

1. T4 cannot alter anything under `/etc`, `/usr`, or any `*.policy`/sandbox conf.
2. The broker is the only path for *consequential* capability execution.
3. Log/ledger writes pass through redaction (`miso/ledger/redact_secrets.py`).
4. No component reads `/etc/shadow` or key stores at T3/T4.
