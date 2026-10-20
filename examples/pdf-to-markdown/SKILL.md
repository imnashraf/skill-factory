---
name: pdf-to-markdown
description: "Extracts and converts PDF document text and tables into clean Markdown format with structured headings when requested."
compatibility: "Designed for Claude Code, Cursor, OpenAI Codex and Google Antigravity."
---

# pdf-to-markdown

## When to use

Use this skill when: Extracts and converts PDF document text and tables into clean Markdown format with structured headings when requested.

## Workflow

1. Clarify expected inputs and outputs.
2. Inspect available files without modifying them.
3. Plan and execute the core task logic.
4. Verify the output and report any limitations.

## Script Invocation

Execute the file transformation script:

```bash
python3 scripts/main.py --input <source_file> --output <target_file>
```

Options:

- `--dry-run`: Preview transformation statistics without writing files.
- `--verbose`: Display detailed per-record conversion logs.

See [references/guide.md](references/guide.md) for data schema mappings and options.
See [examples/example.md](examples/example.md) for sample inputs and outputs.

## Safety

- Never overwrite source input files. Write exclusively to the specified `--output` destination.
- Verify output validity and completeness after transformation.
- Validate file size and schema integrity before reporting success.

## Implementation status

Scaffold with test harness. Implement data transformation logic in [scripts/main.py](scripts/main.py).
Run `python3 -m unittest discover -s tests -v` to verify local execution.
