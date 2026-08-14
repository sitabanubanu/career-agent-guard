#!/usr/bin/env python3
"""Apply deterministic pre-screening rules; this script never authorizes external actions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value)


def _norm(value: Any) -> str:
    return re.sub(r"\s+", "", _text(value)).lower()


def _years(value: Any) -> int | None:
    match = re.search(r"(\d+)\s*(?:年以上|年经验|年)", _text(value))
    return int(match.group(1)) if match else None


def _salary_low(value: Any) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*[kK万]", _text(value))
    if not match:
        return None
    number = float(match.group(1))
    return number * 10 if "万" in match.group(0) else number


def evaluate(profile: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    target = profile.get("target", {})
    constraints = profile.get("constraints", {})
    job = record.get("job", record)
    title = _text(job.get("title"))
    jd = _text(job.get("jd_text"))
    company = _text(job.get("company"))
    full_text = _norm(f"{title} {jd}")
    hard: list[dict[str, Any]] = []
    unknowns: list[str] = []
    risks: list[str] = []

    if not title or not company:
        unknowns.append("title or company is missing")
    if not jd:
        unknowns.append("full JD is missing")

    allowed_types = [_norm(item) for item in target.get("employment_types", [])]
    job_type = _norm(job.get("employment_type"))
    if allowed_types and not job_type:
        unknowns.append("employment_type is missing")
    elif allowed_types and job_type not in allowed_types:
        hard.append({"name": "employment_type", "status": "reject", "value": job.get("employment_type")})
    else:
        hard.append({"name": "employment_type", "status": "pass", "value": job.get("employment_type")})

    allowed_cities = [_norm(item) for item in target.get("locations", [])]
    city = _norm(job.get("city"))
    if allowed_cities and not city:
        unknowns.append("city is missing")
    elif allowed_cities and not any(item in city or city in item for item in allowed_cities):
        hard.append({"name": "location", "status": "reject", "value": job.get("city")})
    else:
        hard.append({"name": "location", "status": "pass", "value": job.get("city")})

    max_required = constraints.get("max_required_experience_years")
    required_years = _years(job.get("experience_text"))
    if max_required is not None and required_years is not None and required_years > max_required:
        hard.append({"name": "experience", "status": "reject", "required_years": required_years})
    elif max_required is not None and not _text(job.get("experience_text")):
        unknowns.append("experience requirement is missing")
    else:
        hard.append({"name": "experience", "status": "pass", "required_years": required_years})

    excluded = [_norm(item) for item in constraints.get("excluded_keywords", [])]
    matched_exclusions = [item for item in excluded if item and item in full_text]
    if matched_exclusions:
        hard.append({"name": "excluded_keywords", "status": "reject", "matched": matched_exclusions})
    else:
        hard.append({"name": "excluded_keywords", "status": "pass"})

    salary_floor = constraints.get("salary_floor_k")
    salary_low = _salary_low(job.get("salary_text"))
    if salary_floor is not None and salary_low is None:
        unknowns.append("salary cannot be parsed against the configured floor")
    elif salary_floor is not None and salary_low < float(salary_floor):
        hard.append({"name": "salary", "status": "reject", "salary_low_k": salary_low})
    elif salary_floor is not None:
        hard.append({"name": "salary", "status": "pass", "salary_low_k": salary_low})

    role_terms = [_norm(item) for item in target.get("role_families", [])]
    role_hits = [term for term in role_terms if term and term in _norm(title + " " + jd)]
    skills = [_norm(item) for item in target.get("skills", [])]
    skill_hits = [skill for skill in skills if skill and skill in full_text]
    fit_score = min(100, (40 if role_hits else 0) + (30 * len(skill_hits) // max(1, len(skills)) if skills else 15) + (20 if jd else 0) + (10 if company else 0))
    if not role_hits:
        risks.append("no configured role-family term was found; review the full JD")

    has_reject = any(item.get("status") == "reject" for item in hard)
    decision = "REJECT" if has_reject else ("HOLD" if unknowns else "PASS")
    return {
        "schema_version": 1,
        "policy_version": "career-agent-guard-v1",
        "job_fingerprint": record.get("provenance", {}).get("raw_fingerprint"),
        "decision": decision,
        "hard_gates": hard,
        "fit_factors": {"role_hits": role_hits, "skill_hits": skill_hits},
        "fit_score": fit_score,
        "unknowns": unknowns,
        "risks": risks,
        "action_allowed": False,
        "action_status": "not_started",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("job", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        record = json.loads(args.job.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": f"cannot read input: {exc}"}, ensure_ascii=False))
        return 2
    if not isinstance(profile, dict) or not isinstance(record, dict):
        print(json.dumps({"error": "profile and job must be JSON objects"}, ensure_ascii=False))
        return 2
    result = evaluate(profile, record)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
