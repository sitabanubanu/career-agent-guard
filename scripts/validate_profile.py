#!/usr/bin/env python3
"""Validate a career-agent-guard candidate profile without printing its contents."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SECRET_KEY_RE = re.compile(
    r"(?:password|passwd|cookie|token|secret|api[_-]?key|access[_-]?token|authorization|bst)",
    re.IGNORECASE,
)
FACT_STATUSES = {"verified", "inferred", "unknown"}


def _contains_secret_key(value: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if SECRET_KEY_RE.search(str(key)):
                found.append(child_path)
            found.extend(_contains_secret_key(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_contains_secret_key(child, f"{path}[{index}]"))
    return found


def validate(profile: Any) -> list[str]:
    issues: list[str] = []
    if not isinstance(profile, dict):
        return ["root must be a JSON object"]

    if profile.get("schema_version") != 1:
        issues.append("schema_version must be 1")
    for field in ("profile_id", "facts", "target", "constraints", "consent"):
        if field not in profile:
            issues.append(f"missing required field: {field}")

    if not isinstance(profile.get("facts"), list):
        issues.append("facts must be a list")
    else:
        for index, fact in enumerate(profile["facts"]):
            if not isinstance(fact, dict):
                issues.append(f"facts[{index}] must be an object")
                continue
            for field in ("claim", "source", "status"):
                if not fact.get(field):
                    issues.append(f"facts[{index}].{field} is required")
            if fact.get("status") not in FACT_STATUSES:
                issues.append(f"facts[{index}].status must be verified, inferred, or unknown")

    target = profile.get("target")
    if not isinstance(target, dict):
        issues.append("target must be an object")
    else:
        for field in ("role_families", "employment_types", "locations"):
            if not isinstance(target.get(field), list):
                issues.append(f"target.{field} must be a list")
        if not target.get("role_families"):
            issues.append("target.role_families must not be empty")

    constraints = profile.get("constraints")
    if not isinstance(constraints, dict):
        issues.append("constraints must be an object")
    elif constraints.get("unknown_hard_gate_action", "hold") not in {"hold", "reject"}:
        issues.append("constraints.unknown_hard_gate_action must be hold or reject")

    consent = profile.get("consent")
    if not isinstance(consent, dict):
        issues.append("consent must be an object")
    else:
        for field in ("allowed_platforms", "allowed_actions", "require_approval_for"):
            if not isinstance(consent.get(field), list):
                issues.append(f"consent.{field} must be a list")
        batch_size = consent.get("max_batch_size")
        if not isinstance(batch_size, int) or batch_size < 1:
            issues.append("consent.max_batch_size must be a positive integer")

    secret_paths = _contains_secret_key(profile)
    if secret_paths:
        issues.append("forbidden secret-like keys present: " + ", ".join(secret_paths[:8]))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    args = parser.parse_args()
    try:
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "issues": [f"cannot read profile: {exc}"]}, ensure_ascii=False))
        return 2

    issues = validate(profile)
    result = {"valid": not issues, "issue_count": len(issues), "issues": issues}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not issues else 2


if __name__ == "__main__":
    sys.exit(main())
