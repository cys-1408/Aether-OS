"""Minimal stdlib JSON-Schema (draft-07 subset) validator.

Supported keywords: type, properties, required, items, enum, minimum, maximum,
minLength, maxLength, minItems, maxItems, pattern, additionalProperties,
anyOf, allOf, oneOf (count==1), and local $ref ({"$ref": "#/definitions/x"}).
Raises AetherError on violation with the instance path.
"""
from __future__ import annotations

from typing import Any
from .errors import AetherError


def _resolve(schema: dict, root: dict) -> dict:
    if isinstance(schema, dict) and "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise AetherError("E_SCHEMA_REF", f"only local $ref supported: {ref}")
        node: Any = root
        for part in ref[2:].split("/"):
            node = node[part]
        return node
    return schema


def _check_type(value: Any, t, path: str) -> None:
    type_map = {
        "object": dict, "array": list, "string": str, "boolean": bool,
        "null": type(None),
    }
    if t == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            raise AetherError("E_SCHEMA_TYPE", f"{path}: expected integer")
        return
    if t == "number":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise AetherError("E_SCHEMA_TYPE", f"{path}: expected number")
        return
    if t not in type_map:
        raise AetherError("E_SCHEMA_KEYWORD", f"{path}: unknown type {t!r}")
    if isinstance(value, bool) and t in ("string", "object", "array", "null"):
        raise AetherError("E_SCHEMA_TYPE", f"{path}: expected {t}")
    if not isinstance(value, type_map[t]):
        raise AetherError("E_SCHEMA_TYPE", f"{path}: expected {t}")


def validate(instance: Any, schema: dict, *, root: dict | None = None, path: str = "$") -> None:
    root = root if root is not None else schema
    schema = _resolve(schema, root)
    if schema is True:
        return
    if schema is False or not isinstance(schema, dict):
        raise AetherError("E_SCHEMA_FALSE", f"{path}: schema forbids value")

    if "type" in schema:
        t = schema["type"]
        ts = t if isinstance(t, list) else [t]
        last = None
        for one in ts:
            try:
                _check_type(instance, one, path)
                break
            except AetherError as e:
                last = e
        else:
            raise last  # type: ignore[misc]

    if "enum" in schema and instance not in schema["enum"]:
        raise AetherError("E_SCHEMA_ENUM", f"{path}: not in enum {schema['enum']!r}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise AetherError("E_SCHEMA_MINLEN", f"{path}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            raise AetherError("E_SCHEMA_MAXLEN", f"{path}: longer than {schema['maxLength']}")
        if "pattern" in schema:
            import re
            if not re.search(schema["pattern"], instance):
                raise AetherError("E_SCHEMA_PATTERN", f"{path}: fails pattern {schema['pattern']!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            raise AetherError("E_SCHEMA_MIN", f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            raise AetherError("E_SCHEMA_MAX", f"{path}: above maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            raise AetherError("E_SCHEMA_MINITEMS", f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            raise AetherError("E_SCHEMA_MAXITEMS", f"{path}: more than {schema['maxItems']} items")
        if "items" in schema:
            for i, item in enumerate(instance):
                validate(item, schema["items"], root=root, path=f"{path}[{i}]")

    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                raise AetherError("E_SCHEMA_REQUIRED", f"{path}: missing required {req!r}")
        props = schema.get("properties", {})
        for key, val in instance.items():
            if key in props:
                validate(val, props[key], root=root, path=f"{path}.{key}")
            else:
                ap = schema.get("additionalProperties", True)
                if ap is False:
                    raise AetherError("E_SCHEMA_ADDL", f"{path}: unexpected property {key!r}")
                if isinstance(ap, dict):
                    validate(val, ap, root=root, path=f"{path}.{key}")

    for keyword in ("anyOf", "oneOf", "allOf"):
        if keyword in schema:
            subs = schema[keyword]
            if keyword == "allOf":
                for i, sub in enumerate(subs):
                    validate(instance, sub, root=root, path=f"{path} (allOf/{i})")
            else:
                passed = 0
                for sub in subs:
                    try:
                        validate(instance, sub, root=root, path=f"{path} ({keyword})")
                        passed += 1
                    except AetherError:
                        pass
                if keyword == "anyOf" and passed < 1:
                    raise AetherError("E_SCHEMA_ANYOF", f"{path}: matches no anyOf branch")
                if keyword == "oneOf" and passed != 1:
                    raise AetherError("E_SCHEMA_ONEOF", f"{path}: matches {passed} oneOf branches")
