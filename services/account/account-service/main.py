"""aether-account-service — unprivileged facade over the polkit helper."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))

from service_main import SystemService  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402
import user_create, group_policy  # noqa: E402
from account_events import log_event  # noqa: E402


def list_users() -> dict:
    import pwd
    users = []
    for entry in pwd.getpwall():
        if entry.pw_uid >= 1000 or entry.pw_name == "root":
            users.append({"username": entry.pw_name, "uid": entry.pw_uid,
                          "full_name": entry.pw_gecos.split(",")[0],
                          "home": entry.pw_dir, "shell": entry.pw_shell,
                          "groups": group_policy.user_groups(entry.pw_name)})
    return {"users": users}


def build_service() -> SystemService:
    svc = SystemService("account", "account", {
        "Accounts.list": lambda p: list_users(),
        "Accounts.create": lambda p: user_create.create_user(
            str(p.get("username", "")), str(p.get("full_name", "")),
            str(p.get("password", "")), bool(p.get("admin", False))),
        "Accounts.set_password": lambda p: user_create.set_password(
            str(p.get("username", "")), str(p.get("password", ""))),
        "Accounts.groups": lambda p: {"groups": group_policy.user_groups(str(p.get("username", "")))},
        "Accounts.add_group": lambda p: group_policy.add_to_group(
            str(p.get("username", "")), str(p.get("group", ""))),
        "Accounts.password_policy": lambda p: {"policy": user_create.password_score(p.get("password", ""))},
    })
    return svc


if __name__ == "__main__":
    svc = build_service()
    log_event(svc.log, "service_started")
    svc.run()
