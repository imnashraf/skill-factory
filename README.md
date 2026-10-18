# Skill Factory

Free, MIT-licensed, offline Agent Skill scaffold generator. **No API key, subscription, or third-party Python dependency required for the CLI.**

## Quick start

Requires Python 3.9+.

```bash
python3 scripts/create_skill.py --name excel-comparison --description "Compare two Excel files and report differences"
python3 -m unittest discover -s tests -v
```

Output: `generated-skills/excel-comparison/SKILL.md`, `README.md`, `scripts/`, `tests/`, `references/`.

**Important:** The CLI creates a starter structure, not an AI-generated working solution. To build the actual requested behavior, open this repository in a compatible coding agent and ask it to use the `skill-factory` skill. The coding agent may require its own account or subscription.

## Install Skill Factory in an agent

Copy the entire repository folder (or its `SKILL.md` plus `scripts/` and `tests/`) to the agent's supported skills directory. Check that agent's documentation for current paths and restart/reload if necessary. Do not execute unknown scripts without inspecting them.

## Supported approach

Based on the open Agent Skills specification: https://agentskills.io/specification. Claude Code, Cursor, Codex and Antigravity integrations require separate installation verification; no one-click integration is claimed yet.

## Roadmap

- Platform detection and safe local installer (with explicit permission)
- Guided no-code interface
- Functional generation and test evaluation in a connected agent
- Verified per-platform install packages and release downloads
- GitHub release automation and security scanning

## Safety

No network access, no telemetry, no overwrite, no destructive changes in the scaffold generator.
