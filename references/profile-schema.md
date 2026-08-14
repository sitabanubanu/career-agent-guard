# Candidate Profile Contract

Use a versioned JSON document. Keep immutable facts separate from preferences and authorization.

```json
{
  "schema_version": 1,
  "profile_id": "candidate-local-id",
  "facts": [
    {
      "claim": "参与电商业务分析与 AI 决策支持",
      "source": "C:/path/to/source.docx",
      "evidence": "原文页码或段落定位",
      "status": "verified",
      "allowed_uses": ["screening", "resume", "message"]
    }
  ],
  "target": {
    "role_families": ["业务分析", "AI 实施", "解决方案顾问"],
    "employment_types": ["internship"],
    "locations": ["上海", "杭州"],
    "remote_allowed": false
  },
  "constraints": {
    "salary_floor_k": null,
    "max_required_experience_years": 2,
    "excluded_keywords": ["纯销售", "高频出差"],
    "unknown_hard_gate_action": "hold"
  },
  "resume_variants": [
    {"id": "ai-solutions", "source": "C:/path/to/resume.pdf", "allowed_roles": ["AI 实施", "解决方案顾问"]}
  ],
  "consent": {
    "allowed_platforms": ["zhipin", "official-career-sites"],
    "allowed_actions": ["search", "read", "draft"],
    "require_approval_for": ["send_greeting", "submit_application", "upload_resume"],
    "max_batch_size": 5
  }
}
```

Rules:

- `verified` claims may be used. `inferred` claims require explicit confirmation before entering a resume or message. `unknown` claims cannot satisfy a hard gate.
- Store source paths and evidence locations, not copies of secrets.
- Keep phone numbers, email addresses, account identifiers, cookies, tokens, and credentials outside this profile unless a specific form requires them at execution time.
- Never use a preference as if it were a fact, and never use a generated resume sentence as evidence.
