# git-release-helper

Automates GitHub release preparation, changelog extraction, and semantic version tagging when releasing software.

## Operational Runbook Overview

This skill provides an interactive, safe, step-by-step operational procedure for managing git-release-helper.

## Runbook Structure

- `SKILL.md`: Interactive agent runbook with pre-flight, execution, and rollback steps
- `references/guide.md`: Detailed troubleshooting steps, environment variables, and rollback specifics
- `examples/example.md`: Walkthrough of standard and rollback runbook scenarios

## Compatibility

| Platform | Supported Path | Invocation |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | `/git-release-helper` |
| Cursor | `.agents/skills/`, `.cursor/skills/` | `/git-release-helper` |
| OpenAI Codex | `.agents/skills/` | `$git-release-helper` |
| Google Antigravity | `.agents/skills/` | `Natural language / model decides` |

## License

Distributed under the MIT license.
