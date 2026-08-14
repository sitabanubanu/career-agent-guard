#!/usr/bin/env python3
"""Create a compact, secret-free audit receipt from a policy decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def create_audit(decision: dict[str, Any], mode: str, action_status: str) -> dict[str, Any]:
    return {
        "audit_schema_version": 1,
        "audit_id": "audit-" + _fingerprint({"decision": decision, "time": datetime.now(timezone.utc).isoformat()})[7:19],
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "policy_version": decision.get("policy_version", "career-agent-guard-v1"),
        "job_fingerprint": decision.get("job_fingerprint"),
        "decision": decision.get("decision", "UNKNOWN"),
        "decision_reasons": {
            "hard_gates": decision.get("hard_gates", []),
            "unknowns": decision.get("unknowns", []),
            "risks": decision.get("risks", []),
        },
        "fit_score": decision.get("fit_score"),
        "action": {"type": "none", "status": action_status},
        "verification": {"status": "not_applicable", "evidence": []},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision", type=Path)
    parser.add_argument("--mode", default="analyze", choices=("observe", "analyze", "draft", "confirm", "execute"))
    parser.add_argument("--action-status", default="not_started", choices=("not_started", "draft", "approved", "executed", "verified", "failed", "blocked", "unknown"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        decision = json.loads(args.decision.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": f"cannot read decision: {exc}"}, ensure_ascii=False))
        return 2
    if not isinstance(decision, dict):
        print(json.dumps({"error": "decision must be a JSON object"}, ensure_ascii=False))
        return 2
    result = create_audit(decision, args.mode, args.action_status)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
