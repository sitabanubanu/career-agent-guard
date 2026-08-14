#!/usr/bin/env python3
"""Normalize a raw job JSON object while preserving provenance and minimizing data."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECRET_WORDS = ("password", "cookie", "token", "secret", "api_key", "access_token", "authorization", "bst")


def _safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _safe_value(child)
            for key, child in value.items()
            if not any(word in str(key).lower() for word in SECRET_WORDS)
        }
    if isinstance(value, list):
        return [_safe_value(child) for child in value]
    return value


def _first(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value not in (None, "", []):
            return value
    return None


def _text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value).strip() or None


def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    source = raw.get("source") if isinstance(raw.get("source"), dict) else {}
    payload = raw.get("job") if isinstance(raw.get("job"), dict) else raw
    safe_raw = _safe_value(raw)
    fingerprint = hashlib.sha256(
        json.dumps(safe_raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    retrieved_at = _first(source, "retrieved_at") or datetime.now(timezone.utc).isoformat()

    return {
        "schema_version": 1,
        "source": {
            "platform": _text(_first(source, "platform") or raw.get("platform")) or "unknown",
            "url": _text(_first(source, "url") or _first(payload, "url", "link", "jobUrl")),
            "retrieved_at": retrieved_at,
        },
        "identifiers": {
            "job_id": _text(_first(payload, "job_id", "jobId", "encryptJobId", "lid")),
            "company_id": _text(_first(payload, "company_id", "companyId", "encryptBrandId")),
        },
        "job": {
            "title": _text(_first(payload, "title", "jobName", "positionName")),
            "company": _text(_first(payload, "company", "companyName", "brandName")),
            "employment_type": _text(_first(payload, "employment_type", "employmentType", "jobType")),
            "city": _text(_first(payload, "city", "cityName", "locationName")),
            "salary_text": _text(_first(payload, "salary_text", "salary", "salaryDesc")),
            "experience_text": _text(_first(payload, "experience_text", "experience", "jobExperience")),
            "education_text": _text(_first(payload, "education_text", "education", "jobDegree")),
            "jd_text": _text(_first(payload, "jd_text", "jobDescription", "postDescription", "description")),
            "skills": _first(payload, "skills", "jobLabels", "labels") or [],
        },
        "provenance": {
            "raw_fingerprint": f"sha256:{fingerprint}",
            "field_evidence": raw.get("field_evidence", {}),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": f"cannot read input: {exc}"}, ensure_ascii=False))
        return 2
    if not isinstance(raw, dict):
        print(json.dumps({"error": "input must be a JSON object"}, ensure_ascii=False))
        return 2

    result = normalize(raw)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
