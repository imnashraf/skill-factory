# Skill Factory — Public Launch Preparation Kit

This document provides a launch kit for introducing Skill Factory to developers, AI practitioners, and open-source communities. All materials strictly reflect the tested, local-first capabilities of Skill Factory and avoid unsupported marketing claims.

---

## 1. Project Metadata & GitHub Presentation

### Tagline / Short Description

> "A local-first, zero-dependency toolkit for building, validating, testing, and installing reusable skills across AI coding assistants."

### Suggested GitHub Topics

- `ai-agents`
- `ai-coding-assistant`
- `claude-code`
- `antigravity`
- `cursor`
- `developer-tools`
- `local-first`
- `python`
- `security-scanner`
- `skills`

### Core Value Proposition

1. **Local-First & Offline:** Pure Python standard library implementation. No mandatory accounts, telemetry, API tokens, or cloud servers.
2. **Deterministic Lifecycle:** Comprehensive scaffolding, semantic validation, static security auditing, manifest hashing, atomic installation, and clean rollback.
3. **Cross-Platform & Cross-Assistant:** Standardized skill package structure compatible with Claude Code, Google Antigravity, Cursor, and OpenAI Codex conventions.

---

## 2. Release Announcement Draft (v1.0.1)

````markdown
# Skill Factory v1.0.1: Build, Validate, and Install AI Coding Assistant Skills

Skill Factory provides a standard, repeatable toolkit to create, test, and safely install reusable skills for AI coding assistants.

### Highlights:
- **Zero Runtime Dependencies:** Runs on pure Python standard library (Python 3.9+).
- **Five Pre-Packaged Reference Skills:**
  - `excel-comparison`: Fast row/cell-level CSV & XLSX diffing.
  - `security-config-scanner`: Detects exposed secrets, API keys, and insecure settings.
  - `file-organizer`: Structured directory organization with collision handling.
  - `csv-to-report`: Statistical data profiling and Markdown/HTML summaries.
  - `markdown-doc-validator`: Audits broken relative links and code fence annotations.
- **Safety by Default:** Static security scanner, manifest SHA-256 integrity verification, collision detection, and atomic rollback on failed installations.
- **Support for Leading AI Assistants:** Target Claude Code, Google Antigravity, Cursor, or OpenAI Codex with explicit project or user scopes.

### Quick Start:

```bash
pip install git+https://github.com/imnashraf/skill-factory.git
skillfactory new my-skill --category automation
skillfactory validate ./my-skill
```

Check out the full documentation and beginner guide: [Skill Factory GitHub Repository](https://github.com/imnashraf/skill-factory)
````

---

## 3. Community Announcement Drafts

### A. Hacker News ("Show HN")

**Title:** Show HN: Skill Factory – Local-first toolkit to build and install AI agent skills

**Text:**

> Hi HN! We built Skill Factory because developing and sharing custom skills for AI coding assistants (like Claude Code, Cursor, and Google Antigravity) currently suffers from fragmented formats, unvalidated scripts, and manual copy-pasting.
>
> Skill Factory is a local-first, zero-dependency Python toolkit that standardizes the skill lifecycle:
>
> 1. Scaffolding: Generates clean SKILL.md specs, execution scripts, and unit tests.
> 2. Validation & Quality: Checks frontmatter schema, file integrity, and computes a 0–100 quality score.
> 3. Security Auditing: Static AST scanner checks for unsafe subprocess execution, arbitrary evals, and network calls before installation.
> 4. Safe Installation: Manifest-tracked installation with SHA-256 checksums, collision guards, and instant rollback.
>
> It requires zero external libraries (pure standard library) and makes zero external network calls.
>
> Repository: [Skill Factory on GitHub](https://github.com/imnashraf/skill-factory)
>
> We would love your feedback on the architecture, format standardization, and security model!

### B. Reddit (r/Python, r/LocalLLaMA, r/MachineLearning)

**Title:** Skill Factory — A local-first, zero-dependency Python tool to build, audit, and install AI assistant skills

**Text:**

> Most AI coding assistants now support external skills or MCP extensions, but authoring them is often ad-hoc.
>
> Skill Factory provides a consistent standard:
>
> - Built with pure Python standard library (no pip dependencies required at runtime).
> - Includes static security scanning to detect suspicious subprocess calls or prompt injection vectors.
> - Manages installations into assistant configuration paths (`~/.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, etc.) with manifest-backed tracking and atomic rollbacks.
> - Ships with 5 reference skills (Excel/CSV comparison, secret scanner, file organizer, CSV reporter, markdown validator).
>
> Repository: [Skill Factory on GitHub](https://github.com/imnashraf/skill-factory)
>
> Feedback and contributions welcome!

---

## 4. AI Coding Assistant Compatibility Comparison

| Dimension | Claude Code | Google Antigravity | Cursor | OpenAI Codex |
| :--- | :--- | :--- | :--- | :--- |
| **Default User Path** | `~/.claude/skills/` | `~/.gemini/skills/` | `~/.cursor/skills/` | `~/.codex/skills/` |
| **Default Project Path** | `.claude/skills/` | `.agents/skills/` | `.cursor/skills/` | `.codex/skills/` |
| **Directory Discovery** | Verified | Verified | Verified | Verified |
| **Natural Language Activation** | Verified | Verified | Manual prompt invocation | Manual script invocation |
| **Configuration Aliases** | `claude`, `claudecode` | `antigravity`, `gemini` | `cursor` | `codex`, `openai` |
| **Integrity Checks** | SHA-256 Manifest | SHA-256 Manifest | SHA-256 Manifest | SHA-256 Manifest |
| **Rollback Support** | Yes (Atomic) | Yes (Atomic) | Yes (Atomic) | Yes (Atomic) |

*Note: Autonomous activation refers to whether the assistant's runtime engine parses SKILL.md instructions automatically upon relevant user prompts.*

---

## 5. Frequently Asked Questions (FAQ)

### What is a "Skill"?

A skill is a self-contained capability package consisting of:

1. `SKILL.md`: Metadata and instructions telling the AI assistant how and when to use the tool.
2. `scripts/`: Executable scripts implementing the deterministic logic.
3. `tests/`: Automated tests verifying the functionality.

### Does Skill Factory require an internet connection?

No. Skill Factory is strictly local-first and functions entirely offline without telemetry or external API requests.

### Does Skill Factory run generated code automatically?

No. Skill Factory generates code templates and statically audits them. It never executes untrusted code automatically during validation or installation without explicit user request.

### How does rollback work?

Every installation generates a cryptographic manifest (`.manifest.json`) containing SHA-256 checksums of every installed file. When uninstalling or rolling back, Skill Factory verifies file hashes and removes only tracked files, ensuring user-modified files are never silently deleted.

---

## 6. Pre-Launch Checklist

- [x] Repository README clearly communicates value proposition and limitations.
- [x] Beginner quick-start guide tested across macOS, Windows, and Linux.
- [x] All 5 reference skill demonstrations validated via `scripts/run_demos.py`.
- [x] Test suite passing with 100% green status across all supported Python versions.
- [x] No secrets, private credentials, or internal test files committed.
- [x] Security reporting policy documented in `SECURITY.md`.
- [x] Contribution workflow and Code of Conduct published.
- [ ] Maintainer authorization obtained before public announcement broadcasts.

---

## 7. User Feedback Collection Process

To capture community feedback systematically:

1. **GitHub Issues:** Use structured issue forms for bug reports and feature requests.
2. **Discussions:** Enable GitHub Discussions for user questions, skill ideas, and community showcase.
3. **Usability Log:** Record beginner pain points in `docs/` to guide future UX refinements.
