# Audit Receipt Contract

Write one record per run and one decision entry per job. Never put secrets in the receipt.

```json
{
  "audit_schema_version": 1,
  "audit_id": "audit-...",
  "recorded_at": "2026-08-14T10:00:00+08:00",
  "mode": "analyze",
  "policy_version": "career-agent-guard-v1",
  "profile_id": "candidate-local-id",
  "job_fingerprint": "sha256:...",
  "decision": "PASS|REJECT|HOLD",
  "decision_reasons": [],
  "evidence_refs": [],
  "action": {"type": "none", "status": "not_started"},
  "verification": {"status": "not_applicable", "evidence": []}
}
```

Do not report an action as completed merely because an executor returned without an error. Keep the original decision, approval, execution, and verification states separate.
