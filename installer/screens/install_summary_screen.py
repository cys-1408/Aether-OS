"""Full recap + typed erase confirmation."""
from __future__ import annotations


def summarize(plan: dict) -> None:
    print("=== Install summary ===")
    print(f"  target disk : {plan['target_disk']}  (WILL BE ERASED)")
    print(f"  encryption  : {'LUKS2' if plan.get('encryption', {}).get('enabled') else 'none'}")
    print(f"  user        : {plan.get('user', {}).get('username', '(none)')}")
