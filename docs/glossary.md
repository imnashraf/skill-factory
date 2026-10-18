# Beginner's Glossary of Agent Skills & Skill Factory

Welcome to the Skill Factory Glossary! If you are new to AI coding assistants or the Agent Skills open standard, this guide explains every key term in plain, simple English without confusing jargon (AC7.05).

---

## Core Concepts

### 1. Agent Skill

An **Agent Skill** is a lightweight, portable folder of instructions, scripts, and documentation that teaches an AI coding assistant (like Claude Code, Cursor, OpenAI Codex, or Google Antigravity) how to perform a specialized software task accurately and repeatably.

### 2. `SKILL.md`

The main instruction file located at the root of every skill folder. It tells the AI assistant:

- What the skill does.
- When to automatically trigger and use it.
- The step-by-step procedure to follow when completing user requests.

### 3. YAML Frontmatter

The metadata header at the very top of `SKILL.md`, surrounded by three dashes (`---`). It contains structured properties such as:

```yaml
---
name: pdf-to-markdown
description: Extracts and converts PDF documents into Markdown text.
compatibility: Designed for Claude Code, Cursor, Codex, and Antigravity.
---
```

AI tools read this header first to decide whether a skill applies to the user's current question.

### 4. Progressive Disclosure

An architectural design pattern where only essential instructions are loaded into the AI's prompt at the start. Detailed manuals, API references, or schemas are kept in separate files inside `references/` or `assets/` so they don't consume the AI's memory until explicitly needed.

### 5. Host-AI Mode

A way of using Skill Factory where your active AI assistant (inside Claude Code, Cursor, etc.) reads the Skill Factory instructions and interviews you directly in the chat window, generating the code and files for you interactively.

### 6. Offline Mode

A completely local way of creating skills without contacting any AI service or external internet server. You run `python3 -m skillfactory interview` in your terminal and answer simple questions, or provide a saved questionnaire file (`--answers`).

### 7. SkillSpec

The intermediate blueprint (`skill-spec.json`) representing everything needed to build a skill: its name, description, chosen template family, author, license, and tools.

### 8. Template Family

A starter blueprint tailored to a specific type of task. Skill Factory provides 5 core template families:

1. **python-script**: Executable Python automation with standalone scripts and unit tests.
2. **file-transform**: Converts or cleans documents, logs, or data formats.
3. **checklist-review**: Verification guidelines and audits (e.g., Docker security, accessibility).
4. **workflow-runbook**: Step-by-step procedures for releases, deployments, or migrations.
5. **instructions-only**: Pure guidance and rules for coding style, database migrations, or prompt engineering.

### 9. Platform Adapter

The compatibility bridge that configures a skill so it works seamlessly inside different AI tools, translating folder structures and discovery paths for Claude Code, Cursor, Codex, and Antigravity.

### 10. Discovery Path

The exact folder on your computer where an AI assistant looks for installed skills. For example:

- **Claude Code**: `.claude/skills/<skill-name>/`
- **Cursor / Codex / Antigravity**: `.agents/skills/<skill-name>/`

### 11. Project Scope vs. User Scope

- **Project Scope (`--scope project`)**: Installs the skill only inside your current workspace folder, making it available to anyone working on that specific codebase.
- **User Scope (`--scope user`)**: Installs the skill in your personal user directory (e.g., `~/.claude/skills/` or `~/.agents/skills/`), making it available across all projects on your computer.

### 12. Manifest (`manifest.json`)

A special file stored at `.skillfactory/manifest.json` that records a SHA-256 digital fingerprint (checksum) for every file in the skill. This allows Skill Factory to detect if any files were modified by the user or corrupted.

### 13. Subprocess Test Runner

A safe execution mechanism (`skillfactory test <skill>`) that runs skill tests in a separate, isolated background process with a strict 10-second timeout. This prevents runaway loops or frozen scripts from crashing your terminal.

### 14. AST Safety Scanner

A code inspector (`skillfactory scan <skill>`) that uses Python's Abstract Syntax Tree (AST) to analyze script code without executing it. It detects dangerous operations like `eval()`, `exec()`, `shell=True`, and hardcoded credentials.

### 15. Quality Evaluation Score (`skillfactory eval`)

An objective 0–100 score that rates any skill across 5 dimensions: Structure & Spec Compliance (25 pts), Portability (20 pts), Documentation (20 pts), Test Coverage (20 pts), and Code Safety (15 pts). Scores 90–100 receive **Grade A**.

### 16. Portable Zip Package (`skillfactory export` / `import`)

A reproducible `.zip` archive containing the skill and its SHA-256 checksum. Skill Factory protects against "Zip-Slip" attacks (path traversal exploits) when extracting third-party archives.

### 17. Rollback & Snapshot (`skillfactory rollback`)

A safety net that automatically creates a timestamped backup before updating or removing a skill. If an update breaks your workflow, you can immediately restore the previous version with a single command.
