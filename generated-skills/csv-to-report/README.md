# csv-to-report

Convert CSV data into formatted analytical executive reports in Markdown or HTML.

## Usage

### Transform Files

```bash
python3 scripts/main.py --input data/source.txt --output data/result.txt
```

### Dry Run Preview

```bash
python3 scripts/main.py --input data/source.txt --output data/result.txt --dry-run
```

### Run Tests

```bash
python3 -m unittest discover -s tests -v
```

## Structure

- `SKILL.md`: Agent prompt and conversion procedure
- `scripts/main.py`: File transformation engine
- `tests/test_placeholder.py`: Automated tests verifying structure and conversion
- `references/guide.md`: Schema, format specifications, and error handling
- `examples/example.md`: Before-and-after conversion samples

## Compatibility

| Platform | Supported Path | Invocation |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | `/csv-to-report` |
| Cursor | `.agents/skills/`, `.cursor/skills/` | `/csv-to-report` |
| OpenAI Codex | `.agents/skills/` | `$csv-to-report` |
| Google Antigravity | `.agents/skills/` | `Natural language / model decides` |

## License

Distributed under the MIT license.
