# file-organizer

Organize and rename files into structured directories based on file types, dates, and name patterns.

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
| Claude Code | `.claude/skills/` | `/file-organizer` |
| Cursor | `.agents/skills/`, `.cursor/skills/` | `/file-organizer` |
| OpenAI Codex | `.agents/skills/` | `$file-organizer` |
| Google Antigravity | `.agents/skills/` | `Natural language / model decides` |

## License

Distributed under the MIT license.
