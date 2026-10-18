# docker-security-audit

Audits Dockerfiles and container configurations for root user execution, sensitive volume mounts, and security vulnerabilities.

## Overview
This skill provides a standardized, repeatable inspection and review checklist designed for multi-agent workflows.

## Contents
- `SKILL.md`: Review protocol and inspection checklist
- `references/guide.md`: Detailed inspection standards and severity definitions
- `examples/example.md`: Sample review findings report

## Compatibility
| Platform | Supported Path | Invocation |
|---|---|---|
| Claude Code | `.claude/skills/` | `/docker-security-audit` |
| Cursor | `.agents/skills/`, `.cursor/skills/` | `/docker-security-audit` |
| OpenAI Codex | `.agents/skills/` | `$docker-security-audit` |
| Google Antigravity | `.agents/skills/` | `Natural language / model decides` |

## License
Distributed under the MIT license.
