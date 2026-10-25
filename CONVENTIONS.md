# AetherOS Engineering Contract (BINDING)

This file is the single source of truth for every implementation agent working on AetherOS.
Every agent MUST read this file before writing any code. Deviations must be recorded in the worklog.

## 0. Prime directives

1. **Real code only.** No TODO, FIXME, XXX, NotImplemented, `pass`-only functions, mock data,
   hard-coded fake readings, placeholder screens, or "implement later" comments. Zero matches
   of `TODO|FIXME|NotImplementedError` anywhere in the tree.
2. This is the Aether OS source distribution. It is NOT a website. Every service talks to real
   Linux system interfaces (procfs/sysfs, systemd, nmcli, pactl/wpctl, timedatectl, pacman, sway IPC).
3. If a capability is genuinely unavailable at runtime, services must report that truthfully
   (e.g. `{"supported": false, "reason": "smartctl not installed"}`) — never fabricate data.
4. English everywhere (code, comments, docs, UI strings).

## 1. Repository layout and ownership

Repo root: `/home/z/my-project/download/AetherOS`  (referred to below as `$REPO`)
Each agent owns exclusive directories. NEVER write outside your ownership map.

## 2. Languages and dependencies

| Area | Language | Notes |
|---|---|---|
| System services, daemons, installer logic, recovery, updater, package-manager | Python 3.11+ | stdlib + PyYAML ONLY (declared as `python-yaml` in base packages) |
| Desktop shell + native apps | Python 3 + GTK3 (PyGObject) | `import gi; gi.require_version("Gtk","3.0")`. Vte/GtkSource/Rsvg optional with coded fallbacks |
| Build/boot scripts | POSIX-ish Bash (`set -euo pipefail`) | run on Arch-based build host |
| Shared C libraries | C11 | only under `libraries/` (real, compilable, CMakeLists provided) |
| Config | YAML / JSON / .conf / systemd units | validated at build time |

**Forbidden:** shell-string interpolation of model output, arbitrary `eval`, third-party pip deps
beyond PyYAML in services, `eval()` in Calculator (use the shunting-yard parser), browser tech as the shell.

## 3. Shared Python package `aether_core` (lives at `$REPO/libraries/libaether-core/python/aether_core/`)

Services import it via: `sys.path.insert(0, str(REPO_ROOT / "libraries/libaether-core/python"))`.
Owner (Agent 3) must implement EXACTLY this API:

```python
# result.py
def ok(value) -> dict                 # {"ok": True, "value": value}
def err(code: str, message: str, *, retriable: bool = False, details=None) -> dict
# errors.py
class AetherError(Exception): code, message, retriable, details
class IpcError(AetherError): jsonrpc_code: int
# ipc.py  (JSON-RPC 2.0 over unix domain sockets — THE Aether local IPC, v1)
class JsonRpcServer:
    def __init__(self, socket_path: Path, methods: dict[str, Callable[[dict], dict]],
                 *, socket_mode: int = 0o660, socket_group: str | None = None): ...
    def serve_forever(self) -> None    # blocking; SIGTERM/SIGINT -> clean stop, removes socket
    def stop(self) -> None
def call(socket_path: Path, method: str, params: dict | None = None, *, timeout: float = 10.0) -> dict
    # returns "result" dict; raises IpcError on error frame
# schema.py — minimal stdlib JSON-Schema (draft-07 subset: type, properties, required, items,
#   enum, minimum/maximum, minLength/maxLength, pattern, additionalProperties, anyOf/allOf, $ref-local)
def validate(instance, schema, path="$") -> None   # raises AetherError on violation
# config.py
def load_yaml(path: Path) -> dict                    # supports ${ENV_VAR} expansion
def atomic_write_text(path: Path, text: str) -> None # tmp file + os.replace, fsync
def atomic_write_yaml(path: Path, data: dict) -> None
# cancellation.py
class CancellationToken:
    def cancel(self) -> None; def cancelled(self) -> bool
    def wait(self, timeout: float) -> bool; def scope(self) -> ContextManager
# resource_limits.py
@dataclass class ResourceBudget: max_mem_mb, cpu_percent, max_concurrent, disk_mb
    @classmethod def from_yaml(cls, path: Path, section: str) -> "ResourceBudget"
# logging_setup.py
def configure_logging(service: str, level: str = "INFO") -> None   # journald-friendly stderr
def redact_text(text: str, rules_path: Path | None = None) -> str
# swayipc.py — minimal i3/sway IPC client (stdlib)
class SwayIPC:
    def __init__(self, socket_path: str | None = None)  # default $SWAYSOCK
    def run_command(self, cmd: str) -> list; def get_tree(self) -> dict
    def get_workspaces(self) -> list; def get_outputs(self) -> list
    def subscribe(self, events: list[str], callback) -> None   # blocking loop
# filesops.py — XDG trash + path safety (real, per freedesktop Trash spec)
def safe_join(root: Path, relative: str) -> Path           # rejects traversal
def is_within(path: Path, root: Path) -> bool
def trash(path: Path) -> dict                              # -> {"trashed_to": ..., "info": ...}
def restore(trash_name: str) -> dict                       # conflict -> " (2)" suffix, reported
def list_trash() -> list[dict]
def stable_file_id(path: Path) -> str                      # sha256(dev:inode:size:mtime) hex
# paths.py
REPO, SYSTEM_RUNTIME_DIR = Path("/run/aether"), XDG helpers,
system_socket(name: str) -> Path            # /run/aether/<name>.sock
user_socket(name: str) -> Path              # /run/user/$UID/aether/<name>.sock
USER_CONFIG_DIR ~/.config/aether, USER_STATE_DIR ~/.local/share/aether,
SYSTEM_STATE_DIR /var/lib/aether, SYSTEM_CONFIG_DIR /etc/aether
# version.py
VERSION = "1.0.0"; API_VERSIONS = {"ipc": 1, "runtime": 1, "intentfs": 1, "broker": 1, "ledger": 1, "workspace": 1}
```

## 4. IPC contract (v1: JSON-RPC 2.0 over UDS; D-Bus XMLs are the documented interface contracts)

Envelope: `{"jsonrpc":"2.0","id":<n>,"method":"<Namespace.action>","params":{...}}`
Reply: `{"jsonrpc":"2.0","id":<n>,"result":{...}}` or `{"jsonrpc":"2.0","id":<n>,"error":{"code":<int>,"message":...,"data":{...}}}`.
Handler returns plain dicts; raise `IpcError(code=..., message=...)` for failures.
Auth: `SO_PEERCRED` uid checks; system sockets group-restricted; user sockets under `/run/user/$UID/aether/`.

### System service sockets (under /run/aether/, daemon creates with umask 0o117)

| Service | Socket name | Namespace | Key methods (implement these names EXACTLY) |
|---|---|---|---|
| hardware-probe | hardware-probe | Hardware | summary, cpu, memory, accelerators, storage, network, thermal, power, profile |
| power-manager | power-manager | Power | status, profiles, set_profile, suspend, battery, thermal |
| account-service | account | Accounts | list, create, set_password, groups (via polkit helper) |
| session | session | Session | status, lock, logout, list |
| mount-manager | storage | Storage | list, mount, unmount, eject, trash, restore, trash_list, disk_health |
| network-service | network | Network | status, wifi_scan, wifi_connect, wifi_disconnect, enable, disable, get_dns, set_dns, vpn_status |
| firewall | firewall | Firewall | status, list_rules, apply_default, validate_rule |
| network-consent | consent | Consent | check, grant, revoke, list |
| audio-service | audio | Audio | status, devices, set_volume, set_default_sink, set_default_source, set_mic_muted |
| voice-input | voice | Voice | status, start_capture, stop_capture |
| clock-service | clock | Clock | now, timezone, set_timezone, locales |
| reminder-service | reminders | Reminders | add, list, remove |
| notification-service | notifications | Notify | notify, list, close, history |
| clipboard-service | clipboard | Clipboard | status, history, clear |
| print-service | printing | Print | status, queue, cancel, devices |
| logging/diagnostics | logs | Logs | query, bundle |
| backup-service | backup | Backup | run, status, verify, restore_preview, restore |
| update-check | updates | Updates | check, status, download, install, history |
| health-service | health | Health | services, summary, events |
| runtime daemon | runtime | Runtime | status, profile, models_list, models_recommend, download_start, download_status, download_cancel, model_remove, warmup, infer, infer_stream, backend_status |
| intentfs | intentfs | IntentFS | search, metadata, status, concepts, reindex, pause, resume, clear, exclusions_get, exclusions_set |
| broker | broker | Broker | capabilities, request, status, history |
| ledger | ledger | Ledger | query, export, clear |
| workspace | workspace | Workspace | save, list, preview_restore, restore, delete |

### User-session sockets (under /run/user/$UID/aether/)

| Service | Socket | Namespace | Methods |
|---|---|---|---|
| aether-shell (desktop) | shell | Shell | capabilities, open_app, close_app, focus_app, list_apps, list_windows, arrange_windows, tile_windows, minimize_window, restore_window, create_workspace, start_focus, pause_focus, end_focus, toast |
| miso agent | agent | Agent | submit, cancel, status, history |
| trash (part of agent-local) | trash | Trash | trash, restore, list |

## 5. Capability IDs (CapabilityOS — exact strings, from the project spec)

apps: `list_apps, open_app, close_app, focus_app, create_workspace`
windows: `list_windows, arrange_windows, tile_windows, minimize_window, restore_window`
files: `search_files, show_file_metadata, open_file, create_folder, copy_file, move_file, rename_file, move_to_trash, restore_from_trash, index_file`
writer: `create_document, open_document, save_draft, summarize_selected_document`
focus: `start_focus_session, pause_focus_session, end_focus_session, start_break`
system: `get_cpu_memory_status, get_storage_status, get_network_status, get_battery_status, get_service_status, read_selected_logs`
models: `get_runtime_status, list_models, recommend_model, start_download, cancel_download, switch_model`
workspaces: `save_workspace, preview_workspace_restore, restore_workspace`
settings: `read_setting, change_setting`

Risk classes: `read_only` (auto-allow, logged), `low_reversible` (auto-allow, toast + ledger + undo where practical),
`write` (confirmation required by default), `destructive` (strong confirmation, some agent-disallowed).
Providers: `desktop` (shell UDS), `agent-local` (agent executes unprivileged in user session),
`system:<service>` (broker forwards to that service). Broker is the ONLY route from Miso to privileged actions.

## 6. Capability catalog files (Agent 7-a owns)

`miso/capability-os/schemas/<group>.capabilities.json` where group ∈ {app, window, files, writer, focus,
system-status, model, workspace, settings}. Top-level shape:
`{"group": ..., "version": "1.0.0", "capabilities": [{"id", "version", "provider", "risk_class", "permission", "timeout_s", "idempotent", "side_effects", "confirmation": "never|policy|always", "input_schema": {...}, "output_schema": {...}, "undo": {"supported": bool, "method": str|null}}]}`

## 7. System users, units, paths

- sysusers (rootfs/etc/sysusers.d/aether-users.conf): `aether-runtime`, `aether-broker`, `aether-intentfs`, `aether-ledger`, `aether-hw`, `aether-health` (system users, nologin). Miso agent + shell run as the logged-in user (user services).
- Unit naming: `aether-<name>.service` under `system/services/`. Targets: `aether-graphical.target`, `aether-installer.target`, `aether-recovery.target`, `aether-firstboot.target`. Timers: `aether-index-reconcile.timer`, `aether-update-check.timer`, `aether-maintenance.timer`, `aether-backup-reminder.timer`.
- Unit hardening baseline: `DynamicUser=no` (dedicated users), `NoNewPrivileges=yes`, `ProtectSystem=strict`, `ProtectHome=` as appropriate, `PrivateTmp=yes`, `RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6` (network services only), `SystemCallFilter=@system-service` where safe, `Restart=on-failure`, `RestartSec=2`, journald logging (stderr).
- Config: system defaults `/etc/aether/*.yaml`; user overrides `~/.config/aether/*.yaml`; system state `/var/lib/aether/`; user state `~/.local/share/aether/` (ledger.db, intentfs.db, workspaces/, trash info, drafts).

## 8. Data schemas (Agent 3 owns `protocols/schemas/`, draft-07)

capability-request, capability-result, action-plan, action-ledger-entry, hardware-profile,
model-profile, inference-request, inference-response, intentfs-record, workspace, notification, diagnostic-bundle.
All `"$id": "https://aether-os.org/schemas/<name>.schema.json"`, `"type":"object"`, real fields matching §4 payloads.
`intentfs-record` MUST carry `"concepts": array of exactly 3 strings` when `index_status == "ready"`.

## 9. Desktop theme tokens (from approved aether-ui.html — reproduce EXACTLY)

```
ink:#292824  muted:#817b70  paper:#fffdf8  line:#e8e1d6  orange:#d98250  green:#7c9080  blue:#8fa9c4
desktop bg: radial(#fffdf8 @15% 12%), radial(#d2ccbf @80% 80%), linear 135deg #f2eee5 -> #e4dfd4
top bar: h43px, bg #ffffff7a, blur; windows: radius 16, bg #fffdf9ed, border #fff, shadow 0 18px 55px #40392c20;
active window ring #d9825055; titlebar h40 #fffdf9; traffic dots #ff5f57/#ffbd2e/#28ca41 (11px);
taskbar h60 bg #fffdf8b8; cards #f5f0e6 border #ece3d4 radius 12; btn dark #292824, orange #d98250, soft #f0e9de;
terminal/code bg #262a30 fg #e9e3d9; focus chip dark pill; toasts dark; accents: writer #f2d7c4 files #d9e4d6
terminal #c9d7de code #d8d1e8 clock/timer #dbe7f2 calc #efe6d1 gallery #e6d5e0 mines #d9cdd4 monitor #cfd8cf settings #cfc8bd
MOTION: tail 2s ease-in-out (walk 1s, search .5s, sleep 4s), head 5s, walkBob .5s (run .3s), jump .65s ease-out,
panel .25s, window transitions .6s cubic-bezier(.2,.7,.2,1), toast 2.6s, bubble 3s. Reduced motion kills all.
```
Miso base SVG: copy the `<svg viewBox="0 0 150 135">...</svg>` block from `/home/z/my-project/upload/aether-ui.html`
(grep for `viewBox="0 0 150 135"`). State variants derive from it (sleep = closed-eye strokes, etc.).
GTK animation via Glib timeout ~30fps updating cairo/rsvg transforms; honor GSettings `org.aether.Shell reduced-motion`.

## 10. Apps / desktop entries / icons

App ids: `org.aether.Apps.{Files,Writer,Terminal,Code,Clock,Focus,Calculator,Gallery,SystemMonitor,Settings,SoftwareCenter,Screenshot,ArchiveManager,BackupCenter,RecoveryCenter,Mines}`.
Desktop entries at `applications/<app>/data/<id>.desktop`; SVG icon per app in the same `data/` dir; each app has `Makefile` (install/uninstall/check), `manifest.yaml` (name, id, version, deps), real persistence per contract.

## 11. Compositor + session

Compositor: **sway** (Wayland). Shell is a GTK3 client using `gtk-layer-shell` when available (import guarded, graceful fallback to normal windows). Window ops go through `aether_core.swayipc` (`SWAYSOCK`). Session: `aether-session.service` -> sway -> `aether-shell` (exec from sway config). Screen lock: `swaylock` integration via `desktop/session/session_lock.py`.

## 12. Model / inference backend (ADR-0005)

Backend: **llama.cpp** (`llama-server`) as an external, pluggable native backend, spawned by the Runtime on 127.0.0.1 ephemeral port, never exposed beyond loopback. Models: GGUF from pinned Hugging Face repos; integrity = sha256 fetched from the HF API (`/api/models/<repo>/tree?recursive=true` -> `lfs.sha256`) verified streamingly after download. Catalog: `ai/catalog/catalog.json` + `catalog.schema.json` (Agent 6). No Ollama. No cloud. AI unavailable => OS fully functional; Miso falls back to deterministic rule-based intent handling.

## 13. Verification every agent MUST run before finishing

```bash
cd $REPO
python3 -m compileall -q <your dirs>          # must be clean
for f in $(rg -l '' --glob '*.sh' <your dirs>); do bash -n "$f"; done
python3 - <<'EOF'  # validate all .json (and .yaml) in your dirs parse
import json,glob,yaml,sys
for p in glob.glob('<your dirs>/**/*.json', recursive=True): json.load(open(p))
for p in glob.glob('<your dirs>/**/*.yaml', recursive=True)+glob.glob('<your dirs>/**/*.yml', recursive=True): yaml.safe_load(open(p))
print("OK")
EOF
rg -n "TODO|FIXME|XXX|NotImplementedError" <your dirs>   # must be empty
```

## 14. Worklog protocol

Read `/home/z/my-project/worklog.md` before starting. When finished, APPEND (never overwrite) a section:
`---\nTask ID: <id>\nAgent: <name>\nTask: ...\n\nWork Log:\n- ...\n\nStage Summary:\n- ...` including file counts and any documented deviations.
