"""LUKS2 encryption choice with passphrase strength check."""
from __future__ import annotations

import getpass

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services/account/account-service"))
import user_create  # noqa: E402


def ask_encryption_cli() -> dict:
    choice = input("Encrypt root (LUKS2)? [y/N]: ").strip().lower() == "y"
    if not choice:
        return {"enabled": False}
    while True:
        pw = getpass.getpass("Encryption passphrase: ")
        try:
            user_create.validate_password(pw)
            break
        except ValueError as e:
            print(f"  weak: {e}")
    return {"enabled": True, "passphrase": pw}
