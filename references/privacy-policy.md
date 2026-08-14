# Privacy and Data Handling

- Keep raw resumes and personal documents local unless the user explicitly authorizes a named external destination.
- Minimize each model request to fields needed for the current decision.
- Redact passwords, cookies, access tokens, API keys, phone numbers, emails, identity numbers, and session identifiers from logs and audit files.
- Do not package user-specific resumes, job spreadsheets, profile JSON, browser exports, or credentials into the Skill repository.
- Keep source references and hashes where provenance is useful; do not store unnecessary raw copies.
- Treat a browser's existing login state as an execution dependency, not as data to export.
- If a third-party model is used, disclose the destination and stop if the user has not authorized sending the relevant personal fields.
