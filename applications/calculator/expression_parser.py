"""Shunting-yard evaluator: numbers, + - * / and parentheses. NO eval, ever."""
from __future__ import annotations

import re

_TOKEN = re.compile(r"\s*(?:(\d+\.?\d*)|(.))")


_NORMALIZE = {"\u00d7": "*", "\u00f7": "/", "\u2212": "-"}


def evaluate(expression: str) -> float:
    for uni, ascii_op in _NORMALIZE.items():
        expression = expression.replace(uni, ascii_op)
    tokens = []
    for num, op in _TOKEN.findall(expression):
        if num:
            tokens.append(float(num))
        elif op.strip():
            tokens.append(op)
    if not tokens:
        raise ValueError("empty expression")
    out: list = []
    ops: list[str] = []
    prec = {"+": 1, "-": 1, "*": 2, "/": 2}
    prev = None
    for tok in tokens:
        if isinstance(tok, float):
            out.append(tok)
            prev = "n"
            continue
        if tok == "(":
            ops.append(tok)
            prev = "("
            continue
        if tok == ")":
            while ops and ops[-1] != "(":
                out.append(ops.pop())
            if not ops:
                raise ValueError("unbalanced parentheses")
            ops.pop()
            prev = "n"
            continue
        if tok in prec:
            if tok == "-" and (prev is None or prev in ("(", "op")):
                out.append(0.0)  # unary minus
            elif prev in (None, "(", "op"):
                raise ValueError("misplaced operator")
            while ops and ops[-1] != "(" and prec.get(ops[-1], 0) >= prec[tok]:
                out.append(ops.pop())
            ops.append(tok)
            prev = "op"
            continue
        raise ValueError(f"bad token: {tok!r}")
    while ops:
        op = ops.pop()
        if op == "(":
            raise ValueError("unbalanced parentheses")
        out.append(op)
    st: list[float] = []
    try:
        for tok in out:
            if isinstance(tok, float):
                st.append(tok)
            else:
                if len(st) < 2:
                    raise ValueError("dangling operator")
                b = st.pop()
                a = st.pop()
                st.append(a + b if tok == "+" else a - b if tok == "-" else a * b if tok == "*" else a / b)
    except ZeroDivisionError as e:
        raise ValueError("division by zero") from e
    if len(st) != 1:
        raise ValueError("malformed expression")
    return st[0]
