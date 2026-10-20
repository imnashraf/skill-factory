# excel-comparison

Compares two Excel spreadsheets or CSV files row-by-row and cell-by-cell to identify added, removed, and modified records with detailed diff reports.

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
| Claude Code | `.claude/skills/` | `/excel-comparison` |
| Cursor | `.agents/skills/`, `.cursor/skills/` | `/excel-comparison` |
| OpenAI Codex | `.agents/skills/` | `$excel-comparison` |
| Google Antigravity | `.agents/skills/` | `Natural language / model decides` |

## License

Distributed under the MIT license.
