---
name: docker-security-audit
description: "Audits Dockerfiles and container configurations for root user execution, sensitive volume mounts, and security vulnerabilities."
compatibility: "Designed for Claude Code, Cursor, OpenAI Codex and Google Antigravity."
---

# docker-security-audit

## When to use
Use this skill when: Audits Dockerfiles and container configurations for root user execution, sensitive volume mounts, and security vulnerabilities.

## Review Workflow
1. Clarify expected inputs and outputs.
2. Inspect available files without modifying them.
3. Plan and execute the core task logic.
4. Verify the output and report any limitations.

## Checklist Verification Criteria

### 1. Correctness & Functionality
- Verify that all required inputs are present and meet specifications.
- Ensure outputs match the expected format and structure.
- Check edge-case handling against [references/guide.md](references/guide.md).

### 2. Security & Data Safety
- Ensure no sensitive credentials, secrets, or private keys are exposed.
- Verify safe path operations with no directory traversal risks.
- Ensure external dependencies are minimal and verified.

### 3. Quality & Maintainability
- Confirm compliance with established style standards and guidelines.
- Ensure clear, actionable documentation is present.

## Findings Report Template
When delivering the review summary to the user, format as:
```markdown
# Review Findings: [Target Name]
- Status: [PASS | ACTION REQUIRED | FAIL]
- Critical Issues: [Count]
- Warnings: [Count]

### Detailed Findings
1. [Finding Title] - [Severity: High/Medium/Low]
   - Detail: [Description of issue]
   - Recommendation: [Specific remediation step]
```

## Safety Rules
- Never modify files during a review without explicit user approval.
- Maintain a non-destructive, read-only approach by default.
