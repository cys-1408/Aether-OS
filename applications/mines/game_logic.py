"""Cell rendering + accessibility naming."""
from __future__ import annotations


def cell_label(state: str, n: int) -> tuple[str, str | None]:
    if state == "mine":
        return "●", "mine"
    if state == "number":
        return (str(n) if n else ""), ("rev" if n == 0 else f"n{min(n, 8)}")
    if state == "flag":
        return "⚑", "flagged"
    return "", None


def accessible_name(i: int, state: str, n: int) -> str:
    row, col = divmod(i, 10)
    if state == "hidden":
        return f"cell row {row + 1} column {col + 1}, hidden"
    if state == "flag":
        return f"cell row {row + 1} column {col + 1}, flagged"
    if state == "mine":
        return f"cell row {row + 1} column {col + 1}, mine"
    return f"cell row {row + 1} column {col + 1}, {n or 'no'} adjacent mines"
