"""Catalog cross-check validator (build-time quality gate).

Validates that:
  1. every catalog file parses and satisfies the meta-schema (structural
     fallback when aether_core is not installed on the build host);
  2. every capability id matches the canonical id set from CONVENTIONS §5;
  3. every capability id has an implementation module under
     miso/capabilities/<group>/ and is wired in the execution dispatcher maps
     (parsed from source with ast, so no runtime imports are needed).

Exit code 0 = all checks pass.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "libraries" / "libaether-core" / "python"))
sys.path.insert(0, str(REPO_ROOT))

from aether_core.errors import AetherError  # noqa: E402

from miso.module_loader import load_module  # noqa: E402

CANONICAL_IDS: dict[str, set[str]] = {
    "app": {"list_apps", "open_app", "close_app", "focus_app", "create_workspace"},
    "window": {"list_windows", "arrange_windows", "tile_windows", "minimize_window",
               "restore_window"},
    "files": {"search_files", "show_file_metadata", "open_file", "create_folder",
              "copy_file", "move_file", "rename_file", "move_to_trash",
              "restore_from_trash", "index_file"},
    "writer": {"create_document", "open_document", "save_draft",
               "summarize_selected_document"},
    "focus": {"start_focus_session", "pause_focus_session", "end_focus_session",
              "start_break"},
    "system-status": {"get_cpu_memory_status", "get_storage_status",
                      "get_network_status", "get_battery_status",
                      "get_service_status", "read_selected_logs"},
    "model": {"get_runtime_status", "list_models", "recommend_model",
              "start_download", "cancel_download", "switch_model"},
    "workspace": {"save_workspace", "preview_workspace_restore", "restore_workspace"},
    "settings": {"read_setting", "change_setting"},
}

GROUP_TO_MODULE_DIR = {
    "app": "apps", "window": "windows", "files": "files", "writer": "writer",
    "focus": "focus", "system-status": "system", "model": "models",
    "workspace": "workspaces", "settings": "settings",
}


def extract_literal_dict(source: str, names: set[str]) -> dict:
    """AST-extract module-level literal dict assignments for the given names."""
    tree = ast.parse(source)
    found: dict = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id in names:
            try:
                found[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                continue
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id in names and node.value is not None:
            try:
                found[node.target.id] = ast.literal_eval(node.value)
            except ValueError:
                continue
    return found


def main() -> int:
    failures: list[str] = []

    registry_loader = load_module("miso/capability-os/registry/registry_loader.py")
    catalogs = registry_loader.load_catalogs(None)

    seen_ids: dict[str, str] = {}
    for path, document in catalogs:
        group = document["group"]
        expected = CANONICAL_IDS.get(group)
        if expected is None:
            failures.append(f"{path.name}: unknown catalog group {group!r}")
            continue
        actual = {entry["id"] for entry in document["capabilities"]}
        missing = expected - actual
        extra = actual - expected
        if missing:
            failures.append(f"{path.name}: missing capability ids {sorted(missing)}")
        if extra:
            failures.append(f"{path.name}: unexpected capability ids {sorted(extra)}")
        for cap_id in actual:
            if cap_id in seen_ids:
                failures.append(f"{cap_id}: declared in {seen_ids[cap_id]} and {path.name}")
            seen_ids[cap_id] = path.name

    dispatcher_source = (REPO_ROOT / "miso" / "broker" / "execution_dispatcher.py").read_text(
        encoding="utf-8")
    maps = extract_literal_dict(
        dispatcher_source, {"CAPABILITY_MODULES", "DESKTOP_SHELL_METHODS"})
    capability_modules = maps.get("CAPABILITY_MODULES", {})

    for cap_id in sorted(CANONICAL_IDS):
        module_rel = capability_modules.get(cap_id)
        if module_rel is None:
            failures.append(f"{cap_id}: not wired in execution_dispatcher.CAPABILITY_MODULES")
            continue
        module_file = REPO_ROOT / (module_rel.replace(".", "/") + ".py")
        if not module_file.is_file():
            failures.append(f"{cap_id}: module file missing: {module_file}")

    for group, ids in CANONICAL_IDS.items():
        module_dir = REPO_ROOT / "miso" / "capabilities" / GROUP_TO_MODULE_DIR[group]
        for cap_id in ids:
            expected_file = module_dir / f"{cap_id}.py"
            if not expected_file.is_file():
                failures.append(f"{cap_id}: implementation module missing at {expected_file}")

    if failures:
        print("CAPABILITY CROSS-CHECK FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    total = sum(len(ids) for ids in CANONICAL_IDS.values())
    print(f"capability cross-check OK: {len(seen_ids)}/{total} ids, all wired and implemented")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AetherError as exc:
        print(f"catalog validation error: {exc.message}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as exc:
        print(f"catalog JSON error: {exc}", file=sys.stderr)
        raise SystemExit(2)
