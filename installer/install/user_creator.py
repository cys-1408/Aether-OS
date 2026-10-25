"""UserCreator: create the primary user in the target via useradd + chpasswd."""
from __future__ import annotations

from installer._process import run_argv
from installer.logging.installer_log import InstallerLog
from installer.logging.secret_filter import register_secret


class UserCreator:
    def __init__(self, dry_run: bool = False, log: InstallerLog | None = None):
        self.dry_run = dry_run
        self.log = log or InstallerLog(echo=False)

    def create_user(self, root: str, username: str, full_name: str = "",
                    user_password: str = "", in_wheel_group: bool = True) -> dict:
        if not username or not username.isidentifier() or username[0].isdigit():
            raise ValueError(f"invalid username: {username!r}")
        register_secret(user_password)

        groups = ["users", "wheel"] if in_wheel_group else ["users"]
        argv = ["arch-chroot", root, "useradd", "-m",
                "-c", full_name or username,
                "-G", ",".join(groups),
                "-s", "/bin/bash",
                username]
        res = run_argv(argv, log=self.log, step="users", dry_run=self.dry_run)
        if not res.ok and not self.dry_run:
            raise RuntimeError(f"useradd failed: {res.stderr[-800:]}")

        if user_password and not self.dry_run:
            res = run_argv([*["arch-chroot", root, "chpasswd"]],
                           log=self.log, step="users", dry_run=self.dry_run,
                           input_bytes=f"{username}:{user_password}\n".encode("utf-8"))
            if not res.ok:
                raise RuntimeError(f"chpasswd failed: {res.stderr[-400:]}")
        return {"user": username, "_groups": groups, "wheel": in_wheel_group}
