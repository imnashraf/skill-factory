---
name: security-config-scanner
description: "Scan project directories for exposed credentials, API keys, and insecure configuration settings."
compatibility: "Designed for Claude Code, Cursor, OpenAI Codex and Google Antigravity."
---

# security-config-scanner

## When to use

Use this skill when: Scan project directories for exposed credentials, API keys, and insecure configuration settings.

## Workflow

1. Clarify expected inputs and outputs.
2. Inspect available files without modifying them.
3. Plan and execute the core task logic.
4. Verify the output and report any limitations.

## Script Execution

Run the bundled script to perform the task:

```bash
python3 scripts/main.py --help
```

See [references/guide.md](references/guide.md) for full argument references and options.
See [examples/example.md](examples/example.md) for sample inputs and outputs.

## Safety

- Do not delete or overwrite user data without explicit permission.
- Never send private files to external services.
- Always verify script exit codes before claiming success.

## Implementation status

Scaffold with test harness. Task logic is located in [scripts/main.py](scripts/main.py).
Run `python3 -m unittest discover -s tests -v` to verify local execution.
