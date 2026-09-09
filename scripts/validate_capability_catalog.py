#!/usr/bin/env python3
"""Validate the portable PiPhi capability-catalog contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROLES = ("state", "events", "conditions", "actions")
STATUSES = {"implemented", "planned", "excluded"}
REQUIRED_GROUP_FIELDS = {"id", "status", "scope", "source_refs", "reason", *ROLES}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def validate(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("catalog_version", "integration_id", "coverage_mode", "reviewed_at"):
        if not isinstance(catalog.get(field), str) or not catalog[field].strip():
            errors.append(f"{field} must be a non-empty string")
    if catalog.get("catalog_version") != "1.0":
        errors.append("catalog_version must be 1.0")

    sources = catalog.get("sources")
    if not isinstance(sources, dict) or not sources:
        errors.append("sources must be a non-empty object")
        sources = {}
    elif any(not isinstance(key, str) or not isinstance(value, str) or not value.strip() for key, value in sources.items()):
        errors.append("source keys and values must be non-empty strings")

    groups = catalog.get("groups")
    if not isinstance(groups, list) or not groups:
        return errors + ["groups must be a non-empty array"]

    group_ids: set[str] = set()
    role_ids: dict[str, set[str]] = {role: set() for role in ROLES}
    for index, group in enumerate(groups):
        prefix = f"groups[{index}]"
        if not isinstance(group, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = REQUIRED_GROUP_FIELDS - set(group)
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(sorted(missing))}")
            continue
        group_id = group["id"]
        if not isinstance(group_id, str) or not group_id.strip():
            errors.append(f"{prefix}.id must be a non-empty string")
        elif group_id in group_ids:
            errors.append(f"duplicate group id: {group_id}")
        else:
            group_ids.add(group_id)
        if group["status"] not in STATUSES:
            errors.append(f"{prefix}.status must be implemented, planned, or excluded")
        if not isinstance(group["scope"], list) or not group["scope"]:
            errors.append(f"{prefix}.scope must be a non-empty array")
        if not isinstance(group["reason"], str) or not group["reason"].strip():
            errors.append(f"{prefix}.reason must be a non-empty string")
        refs = group["source_refs"]
        if not isinstance(refs, list) or not refs:
            errors.append(f"{prefix}.source_refs must be a non-empty array")
        else:
            unknown = sorted(ref for ref in refs if ref not in sources)
            if unknown:
                errors.append(f"{prefix}.source_refs unknown: {', '.join(unknown)}")
        for role in ROLES:
            values = group[role]
            if not isinstance(values, list) or any(not isinstance(item, str) or not item.strip() for item in values):
                errors.append(f"{prefix}.{role} must be an array of non-empty strings")
                continue
            duplicates = sorted({item for item in values if values.count(item) > 1})
            for item in duplicates:
                errors.append(f"duplicate {role} id in {prefix}: {item}")
            for item in values:
                if item in role_ids[role]:
                    errors.append(f"duplicate {role} id across groups: {item}")
                role_ids[role].add(item)

    statuses = {group.get("status") for group in groups if isinstance(group, dict)}
    if "implemented" not in statuses:
        errors.append("catalog must contain at least one implemented group")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path, help="path to capability-catalog.json")
    args = parser.parse_args()
    try:
        errors = validate(load_json(args.catalog))
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Capability catalog is valid: {args.catalog}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
