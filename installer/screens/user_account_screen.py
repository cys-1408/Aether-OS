"""Primary user creation (validations shared with the account service)."""
from __future__ import annotations

import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services/account/account-service"))
import user_create  # noqa: E402


def ask_user_cli() -> dict:
    while True:
        username = input("Username: ").strip()
        try:
            user_create.validate_username(username)
            break
        except ValueError as e:
            print(f"  invalid: {e}")
    full = input("Full name: ").strip()
    while True:
        pw = getpass.getpass("Password: ")
        pw2 = getpass.getpass("Confirm password: ")
        if pw != pw2:
            print("  passwords differ"); continue
        try:
            user_create.validate_password(pw)
            break
        except ValueError as e:
            print(f"  weak: {e}")
    admin = input("Administrator (wheel)? [Y/n]: ").strip().lower() != "n"
    return {"username": username, "full_name": full, "password": pw, "admin": admin}
