# Decision Policy

## Order of evaluation

1. Validate source and job identity.
2. Apply hard constraints.
3. Check JD completeness.
4. Evaluate role, skills, experience, education, location, and evidence strength.
5. Produce a recommendation; never authorize an external write from the score alone.

## Hard-gate examples

- Requested employment type is `internship` but the verified job type is full-time: `REJECT`.
- Required experience exceeds the configured candidate boundary: `REJECT` or `HOLD` if the requirement is ambiguous.
- Required city is outside the allowed location set: `REJECT`.
- A configured exclusion is evidenced in the title or JD: `REJECT`.
- A required field cannot be verified: `HOLD`.

## Fit result

Return structured fields:

```json
{
  "decision": "PASS|REJECT|HOLD",
  "hard_gates": [{"name": "employment_type", "status": "pass", "evidence": "job.employment_type"}],
  "fit_factors": [{"name": "skill_overlap", "value": "SQL", "evidence": "job.jd_text"}],
  "unknowns": [],
  "risks": [],
  "fit_score": 0,
  "action_allowed": false
}
```

Use `HOLD` when the conclusion depends on an unverified graduation rule, experience interpretation, employment type, or other hard constraint. AI may summarize and rank; it may not override a hard rejection or convert an unknown into a pass.
