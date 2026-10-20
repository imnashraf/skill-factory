# api-schema-validator

Validates JSON payloads and REST API request bodies against JSON Schema and OpenAPI specifications during API development.

## Getting Started

### 1. Run Automated Tests

```bash
python3 -m unittest discover -s tests -v
```

### 2. Run the Script

```bash
python3 scripts/main.py --help
```

## Structure

- `SKILL.md`: Core agent prompt and instructions
- `scripts/main.py`: Executable task script
- `tests/test_placeholder.py`: Test suite verifying structure and behavior
- `references/guide.md`: Technical documentation and options
- `examples/example.md`: Example inputs and outputs

## Compatibility

| Platform | Supported Path | Invocation |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | `/api-schema-validator` |
| Cursor | `.agents/skills/`, `.cursor/skills/` | `/api-schema-validator` |
| OpenAI Codex | `.agents/skills/` | `$api-schema-validator` |
| Google Antigravity | `.agents/skills/` | `Natural language / model decides` |

## License

Distributed under the MIT license.
