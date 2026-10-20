# Example Review Session for docker-security-audit

## Scenario

Run `docker-security-audit` to achieve: Audits Dockerfiles and container configurations for root user execution, sensitive volume mounts, and security vulnerabilities..

## Sample Review Output

```markdown
# Review Findings: Candidate Artifact

- Status: ACTION REQUIRED
- Critical Issues: 1
- Warnings: 1

### Detailed Findings

1. Unescaped special character in configuration (High)
   - Detail: Configuration parameter contains raw quotes that break downstream parsing.
   - Recommendation: Use double quotes or standard escaping.

2. Documentation gap in README (Low)
   - Detail: Missing quickstart command example.
   - Recommendation: Add a 2-line code snippet showing invocation.
```
