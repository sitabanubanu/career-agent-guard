# Normalized Job Record Contract

Every job must retain source provenance and a stable fingerprint.

```json
{
  "schema_version": 1,
  "source": {"platform": "zhipin", "url": "https://...", "retrieved_at": "2026-08-14T10:00:00+08:00"},
  "identifiers": {"job_id": "platform-id", "company_id": "optional-id"},
  "job": {
    "title": "业务分析实习生",
    "company": "示例公司",
    "employment_type": "internship",
    "city": "上海",
    "salary_text": "150-200元/天",
    "experience_text": "经验不限",
    "education_text": "本科",
    "jd_text": "完整岗位描述",
    "skills": ["Excel", "SQL"]
  },
  "provenance": {
    "raw_fingerprint": "sha256:...",
    "field_evidence": {"title": "source.card.title", "jd_text": "source.detail.postDescription"}
  }
}
```

Required before `PASS`: source URL or file reference, title, company, employment type, and full JD. Missing fields may result in `HOLD`; they must not be silently filled from the title or a keyword.
