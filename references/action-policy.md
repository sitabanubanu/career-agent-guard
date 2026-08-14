# Action and Approval Policy

## Default permissions

| Action | Default |
|---|---|
| Search and read | Allowed in `observe`/`analyze` |
| Normalize and score | Allowed in `analyze` |
| Draft resume or message | Allowed in `draft` |
| Navigate or inspect a browser page | Allowed when scoped to the registered source |
| Send message | Approval required for the exact message and job |
| Upload resume | Approval required for the exact job and resume variant |
| Submit application | Approval required for the exact job and form |
| Exchange contact information | Manual confirmation required |

An approval must be single-purpose, bounded by a batch limit, and expire. A change to the job snapshot, message, resume variant, platform, or action type invalidates the approval.

## Stop conditions

Stop immediately on CAPTCHA, security verification, rate-limit, platform warning, unexpected form fields, account state change, duplicate detection failure, or unverifiable result. Do not evade platform controls, rotate accounts, or switch automation channels to continue.

## Result states

Use `attempted`, `submitted`, `visible_confirmed`, `rejected`, `blocked`, or `unknown`. Only `visible_confirmed` or an equivalent platform-confirmed state may be reported as completed.
