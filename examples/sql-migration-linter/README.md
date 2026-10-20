# sql-migration-linter

Reviews and lints relational database SQL migration scripts for backward-incompatible table locks and dropped columns.

## Overview

This is an instruction-only Agent Skill designed for multi-agent environments including Claude Code, Cursor, Codex, and Antigravity.

## Structure

- `SKILL.md`: Core prompt and instructions for the agent.
- `references/guide.md`: Detailed guidance and domain reference material.
- `examples/example.md`: Practical usage examples.

## Compatibility

| Platform | Supported Path | Invocation |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | `/sql-migration-linter` |
| Cursor | `.agents/skills/`, `.cursor/skills/` | `/sql-migration-linter` |
| OpenAI Codex | `.agents/skills/` | `$sql-migration-linter` |
| Google Antigravity | `.agents/skills/` | `Natural language / model decides` |

## License

Distributed under the MIT license.
