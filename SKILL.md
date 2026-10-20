---
name: skill-factory
description: Create, validate, and package production-ready, multi-agent reusable Agent Skills from user requirements with offline scaffolding, clear safety rules, test generation, and honest capability reporting. Use when a user asks to create, scaffold, inspect, or build an Agent Skill or SKILL.md package.
compatibility: Works with Claude Code, Cursor, OpenAI Codex, and Google Antigravity.
metadata:
  author: "Skill Factory Contributors"
  version: "0.1.0"
---

# Skill Factory

Skill Factory empowers AI assistants and developers to build robust, portable, standard-library-only Agent Skills adhering strictly to the open [Agent Skills Specification](https://agentskills.io/specification).

## When to Use This Skill

Activate this skill whenever the user wants to:

- Create a new Agent Skill from plain English or technical requirements.
- Scaffold a new skill folder with templates, tests, references, and manifest.
- Validate an existing skill for cross-platform compatibility, path safety, and spec compliance.
- Package or prepare a skill for distribution across Claude Code, Cursor, Codex, or Google Antigravity.

---

## The 6-Step Host-AI Creation Loop

When acting as the host AI assistant, execute the following workflow:

### Step 1: Interactive Interview & Requirements Gathering

Ask the user clarifying questions if requirements are underspecified:

1. **Core Problem:** What specific task or capability should this skill provide?
2. **Inputs & Outputs:** What files, arguments, or data formats are expected?
3. **Execution Type:** Does this skill need custom Python scripts (`python-script`, `file-transform`), an inspection checklist (`checklist-review`), an operational playbook (`workflow-runbook`), or pure instructions (`instructions-only`)?
4. **Target Platforms:** Which platforms will use it (Claude Code, Cursor, Codex, Antigravity)?
5. **Edge Cases:** What constraints, boundaries, or failure modes exist?

### Step 2: Formulate the Intermediate Specification (`SkillSpec`)

Convert the gathered requirements into a valid `skill-spec.json`:

- `name`: Lowercase kebab-case, 1–64 characters, avoiding Windows reserved device names (`CON`, `PRN`, `AUX`, `NUL`, etc.) and platform-reserved names (`synced`).
- `description`: 1–1024 characters describing what the skill does and when an agent should trigger it.
- `template_family`: One of `instructions-only`, `python-script`, `checklist-review`, `file-transform`, `workflow-runbook`.
- `steps`: Ordered list of actionable steps.
- `license`: MIT (default), Apache-2.0, Unlicense, or custom.

### Step 3: Atomic Scaffolding

Invoke the Skill Factory CLI to atomically generate the skill directory, template files, and cryptographic manifest:

```bash
python3 -m skillfactory new --name <skill-name> --description "<description>" --template <template-family> --output generated-skills
```

Alternatively, write the specification to `spec.json` and run:

```bash
python3 -m skillfactory new --spec spec.json --output generated-skills
```

### Step 4: Complete Implementation

Flesh out the generated scaffold:

- **Scripts:** If scripts are needed, implement the actual task logic in `scripts/main.py` using Python standard library or well-documented tools.
- **References:** Add detailed technical guides, schema definitions, and background information in `references/guide.md`.
- **Examples:** Provide concrete, realistic input and output examples in `examples/example.md`.

### Step 5: Automated Verification & Linting

Validate the completed skill package:

```bash
python3 -m skillfactory validate generated-skills/<skill-name>
```

Run any automated tests included in the skill:

```bash
python3 -m unittest discover -s generated-skills/<skill-name>/tests -v
```

Fix any syntax errors, link breakages, or test failures before presenting the skill to the user.

### Step 6: Honest Capability Reporting

Deliver a clear summary to the user:

- Present the generated files and structure.
- State whether the skill contains verified working scripts or starter scaffolding.
- Disclose any host model access or platform-specific limitations.
- Note: Skill Factory requires no paid API keys or subscriptions; host assistant interactions use the host environment's existing model capabilities.

---

## Safety & Governance Guidelines

- **Zero Surprises:** Never overwrite existing skills or user directories without explicit permission.
- **Untrusted Code Protection:** Never automatically execute unverified third-party scripts.
- **Privacy First:** All Skill Factory operations run locally and offline. No telemetry or external network calls are made.
