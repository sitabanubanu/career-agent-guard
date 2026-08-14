---
name: career-agent-guard
description: Enforce an evidence-based, privacy-minimizing, approval-gated workflow for job-search agents handling candidate profiles, job listings, tailored resumes, recruiter messages, and browser actions. Use whenever an agent searches, evaluates, drafts, sends, uploads, or verifies job-application or recruiter-contact actions, especially with BOSS, CLI, browser extensions, or company career sites.
---

# Career Agent Guard

Act as the policy and evidence layer for a job-search agent. Do not act as a passive data relay. Carry the same candidate profile, policy version, job record, decision, approval, and verification state through the whole workflow.

## Non-negotiable rules

- Treat explicit source-backed facts, user preferences, inferences, and unknowns as different types of data.
- Never invent, inflate, or silently rewrite education, dates, employers, titles, skills, achievements, eligibility, or salary expectations.
- Apply deterministic hard constraints before probabilistic or AI matching. An unknown hard constraint produces `HOLD`, not `PASS`.
- Treat a score as prioritization only; a score never authorizes an external action.
- Keep drafts separate from sent messages, submitted applications, or uploaded resumes.
- Require an explicit, bounded approval for every external write. Bind approval to the exact platform, job, message, resume variant, and expiry time.
- Never claim success from a click, request, or optimistic UI state alone. Require visible or platform-confirmed evidence and record the evidence.
- Stop on CAPTCHA, security verification, rate-limit, risk warning, changed page structure, missing JD, contradictory data, or unverifiable result. Do not switch channels or accounts to bypass a stop.
- Never place passwords, cookies, access tokens, API keys, or other secrets in a candidate profile, job record, prompt, audit receipt, or packaged skill.

## Operating modes

Use one explicit mode per run:

- `observe`: collect and inspect only; no scoring or drafts are committed.
- `analyze`: normalize jobs, apply hard gates, produce fit decisions and evidence.
- `draft`: create tailored resume/message drafts; do not send or submit.
- `confirm`: show the exact action manifest and wait for user approval.
- `execute`: perform only approved, bounded actions and verify each result.

If the user has not chosen a mode, use `analyze`. Treat `execute` as opt-in for the current batch only; never persist execution permission implicitly.

## Required inputs

Load and validate a candidate profile before processing jobs. The profile must identify:

- verified facts and their source documents;
- target role families, employment types, locations, and salary boundaries;
- hard exclusions and soft preferences;
- allowed resume variants and messaging style;
- permitted platforms and action types;
- batch limits, duplicate policy, and approval requirements.

Use `references/profile-schema.md` for the contract. If required information is missing, report the missing fields and remain read-only.

## Controlled workflow

1. Register the source and retrieval time. Preserve the original job URL or file reference and do not treat a search URL as a job URL.
2. Normalize each job with `scripts/normalize_job.py` or an equivalent schema-preserving adapter. Preserve source IDs and a fingerprint; do not discard unknown fields silently.
3. Run hard gates with `scripts/evaluate_policy.py` or equivalent deterministic logic. Reject only on an evidenced violation. Mark missing or ambiguous hard-gate data as `HOLD`.
4. Read the full JD before fit analysis. Require evidence for role, employment type, experience, education, location, and material skills. Keyword overlap alone is insufficient.
5. Produce a structured decision: `PASS`, `REJECT`, or `HOLD`, with hard-gate results, fit factors, evidence references, uncertainty, and a recommended resume variant. Keep the action flag false.
6. In `draft` mode, generate a message and resume draft from verified claims only. Identify every claim that was emphasized and every material gap.
7. In `confirm` mode, create an action manifest. Show the job, exact message, exact resume, reason for selection, risks, and batch count. Do not execute while approval is pending.
8. In `execute` mode, validate the approval immediately before the action. Pass only an `ActionRequest` accepted by the guard to a CLI, Bridge, BossHelper, or company-site adapter.
9. Verify the result independently. Distinguish `attempted`, `submitted`, `visible_confirmed`, `rejected`, `blocked`, and `unknown`. An unknown result must not be retried automatically.
10. Write an audit receipt without secrets. Use `references/audit-schema.md` and `scripts/create_audit_record.py`.

## Tool boundaries

- Let `boss-agent-cli` search, cache, normalize, and expose read-only candidate data. Do not let its platform adapter bypass the policy decision.
- Let `BOSS Agent Bridge` navigate, inspect, and perform narrowly defined approved page actions. Prefer named operations over arbitrary JavaScript execution.
- Treat `BossHelper`'s direct send, upload, and chat functions as external writes. Wrap them with the same action gate; do not call them merely because a filter or AI score passed.
- Keep OpenCLI, CLI, Bridge, and page extensions as implementation details. None may become a second source of truth for suitability or authorization.

## Action gate contract

Before every external write, require an action request containing at least:

```json
{
  "action_type": "send_greeting",
  "platform": "zhipin",
  "job_id": "platform-job-id",
  "job_fingerprint": "sha256:...",
  "message_fingerprint": "sha256:...",
  "resume_variant": "ai-solutions",
  "approval_id": "approval-...",
  "expires_at": "2026-08-14T12:00:00+08:00"
}
```

Reject the request if the job changed, the approval expired, the message or resume differs, the job was already processed, or the platform reports a safety/rate-limit condition.

## Failure handling

On failure, preserve the last valid state and evidence. Do not silently retry an external write. Retry only read-only acquisition or an explicitly idempotent verification request, within the configured limit. When a tool reports `COMPLIANCE_BLOCKED`, return to analysis or manual completion rather than changing automation channels.

## References and scripts

Read only the reference needed for the current stage:

- `references/profile-schema.md`: candidate facts, preferences, consent, and source rules.
- `references/job-record-schema.md`: normalized job records and provenance.
- `references/decision-policy.md`: hard gates, fit analysis, uncertainty, and decision states.
- `references/action-policy.md`: approval, idempotency, external-write boundaries, and stop conditions.
- `references/privacy-policy.md`: minimization, redaction, retention, and forbidden secrets.
- `references/audit-schema.md`: decision and execution receipts.

Use the bundled scripts for deterministic checks. They are local utilities; they do not contact platforms or upload data.

## Output contract

For each run, return:

1. operating mode and policy version;
2. input and source status;
3. per-job decision with evidence and uncertainty;
4. drafts separately from approved actions;
5. blocked or held items with reasons;
6. execution results only when independently verified;
7. an audit receipt path or structured receipt.

