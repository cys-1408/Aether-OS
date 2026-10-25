"""Strict validation of user-supplied firewall rule specifications.

This is the single source of truth for what a caller may express in
``Firewall.rule_add`` / ``Firewall.validate_rule``.  Anything not explicitly
whitelisted here is rejected with a reason — the firewall never renders
unvalidated text into nftables syntax.
"""
from __future__ import annotations

import ipaddress
import re
from typing import Any

ALLOWED_VERBS = ("accept", "drop", "reject")
ALLOWED_DIRECTIONS = ("input", "output", "forward")
ALLOWED_PROTOCOLS = ("tcp", "udp", "icmp", "icmpv6")
ALLOWED_LIMIT_UNITS = ("second", "minute", "hour")
ALLOWED_FIELDS = (
    "direction", "verb", "protocol", "dport", "sport",
    "source", "destination", "interface", "limit_rate", "limit_unit", "comment",
)
PORT_MIN, PORT_MAX = 1, 65535
_IFACE_RE = re.compile(r"^[A-Za-z0-9._@:-]{1,15}$")
_COMMENT_RE = re.compile(r"^[A-Za-z0-9 ._:@/()-]{0,64}$")


def _validate_port(value: Any, field: str, errors: list[str]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{field} must be an integer between {PORT_MIN} and {PORT_MAX}")
        return None
    if not PORT_MIN <= value <= PORT_MAX:
        errors.append(f"{field}={value} outside {PORT_MIN}..{PORT_MAX}")
        return None
    return value


def _validate_cidr(value: Any, field: str, errors: list[str]) -> str | None:
    if not isinstance(value, str):
        errors.append(f"{field} must be a CIDR string")
        return None
    try:
        net = ipaddress.ip_network(value, strict=False)
    except ValueError:
        errors.append(f"{field}={value!r} is not a valid CIDR")
        return None
    return str(net)


def validate_rule_spec(spec: Any) -> tuple[bool, dict, list[str]]:
    """Validate a rule spec dict.

    Returns ``(ok, normalized, errors)``.  ``normalized`` only contains
    whitelisted fields; ``errors`` lists every violation found.
    """
    errors: list[str] = []
    if not isinstance(spec, dict):
        return False, {}, ["rule spec must be a JSON object"]
    unknown = sorted(set(spec) - set(ALLOWED_FIELDS))
    if unknown:
        errors.append("unknown fields: " + ", ".join(unknown))
        return False, {}, errors

    normalized: dict = {}
    direction = spec.get("direction")
    if direction not in ALLOWED_DIRECTIONS:
        errors.append(f"direction must be one of {ALLOWED_DIRECTIONS}")
    else:
        normalized["direction"] = direction
    verb = spec.get("verb")
    if verb not in ALLOWED_VERBS:
        errors.append(f"verb must be one of {ALLOWED_VERBS}")
    else:
        normalized["verb"] = verb

    protocol = spec.get("protocol")
    if protocol is not None:
        if protocol not in ALLOWED_PROTOCOLS:
            errors.append(f"protocol must be one of {ALLOWED_PROTOCOLS}")
        else:
            normalized["protocol"] = protocol
            if protocol in ("icmp", "icmpv6") and ("dport" in spec or "sport" in spec):
                errors.append("ports are not valid for icmp/icmpv6 rules")

    for field in ("dport", "sport"):
        if field in spec and spec[field] is not None:
            port = _validate_port(spec[field], field, errors)
            if port is not None:
                normalized[field] = port

    for field in ("source", "destination"):
        if field in spec and spec[field] is not None:
            cidr = _validate_cidr(spec[field], field, errors)
            if cidr is not None:
                normalized[field] = cidr

    if "interface" in spec and spec["interface"] is not None:
        iface = spec["interface"]
        if not isinstance(iface, str) or not _IFACE_RE.match(iface):
            errors.append("interface must match [A-Za-z0-9._@:-]{1,15}")
        else:
            normalized["interface"] = iface

    if "limit_rate" in spec and spec["limit_rate"] is not None:
        rate = spec["limit_rate"]
        if isinstance(rate, bool) or not isinstance(rate, int) or not 1 <= rate <= 100000:
            errors.append("limit_rate must be an integer in 1..100000")
        else:
            unit = spec.get("limit_unit", "second")
            if unit not in ALLOWED_LIMIT_UNITS:
                errors.append(f"limit_unit must be one of {ALLOWED_LIMIT_UNITS}")
                return len(errors) == 0, normalized, errors
            normalized["limit_rate"] = rate
            normalized["limit_unit"] = unit

    if "comment" in spec and spec["comment"] is not None:
        comment = spec["comment"]
        if not isinstance(comment, str) or not _COMMENT_RE.match(comment):
            errors.append("comment must match [A-Za-z0-9 ._:@/()-]{0,64}")
        else:
            normalized["comment"] = comment

    return len(errors) == 0, normalized, errors
