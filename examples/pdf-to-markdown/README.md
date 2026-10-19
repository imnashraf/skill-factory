# pdf-to-markdown

Extracts and converts PDF document text and tables into clean Markdown format with structured headings when requested.

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
| Claude Code | `.claude/skills/` | `/pdf-to-markdown` |
| Cursor | `.agents/skills/`, `.cursor/skills/` | `/pdf-to-markdown` |
| OpenAI Codex | `.agents/skills/` | `$pdf-to-markdown` |
| Google Antigravity | `.agents/skills/` | `Natural language / model decides` |

## License

Distributed under the MIT license.
