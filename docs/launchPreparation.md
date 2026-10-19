# Skill Factory — Public Launch Preparation Kit (Phase 15)

This document provides a launch kit for introducing Skill Factory to developers, AI practitioners, and open-source communities. All materials strictly reflect the tested, local-first capabilities of Skill Factory and avoid unsupported marketing claims.

---

## 1. Project Metadata & GitHub Presentation

### Tagline / Short Description

> "A local-first, zero-dependency open-source ecosystem to create, validate, test, install, and share skills across AI coding assistants."

### Suggested GitHub Topics

- `ai-agents`
- `ai-coding-assistant`
- `claude-code`
- `antigravity`
- `cursor`
- `copilot`
- `windsurf`
- `developer-tools`
- `local-first`
- `python`
- `security-scanner`
- `skills`

### Core Value Proposition

1. **Local-First & Offline:** Pure Python standard library implementation. Zero mandatory accounts, telemetry, API tokens, or cloud servers.
2. **Deterministic Lifecycle:** Comprehensive scaffolding, semantic validation, static AST security auditing, manifest hashing, atomic installation, and clean rollback.
3. **Cross-Platform & 8 Assistants:** Standardized skill package structure compatible with Claude Code, Google Antigravity, Cursor, OpenAI Codex, Windsurf, Continue, Cline, and GitHub Copilot.
4. **5 Curated Domain Packs (14 Grade A Skills):** Ready-to-use reference skills across Office Productivity, Finance & ERP, HR & Workforce, Project Management, and Developer & Security.
5. **Optional AI-Assisted Creation:** Provider-neutral natural language skill synthesis (local Ollama, OpenAI-compatible, or mock) with pre-execution AST safety quarantine and bounded self-repair.

---

## 2. Release Announcement Draft (v1.2.0)

````markdown
# Skill Factory v1.2.0: Build, Audit, and Share AI Coding Assistant Skills

Skill Factory transforms how developers and non-programmers create, validate, test, install, and share reusable Agent Skills.

### Highlights in v1.2.0:
- **Zero Runtime Dependencies:** Runs on pure Python standard library (Python 3.9+).
- **8 Supported AI Coding Assistants:** Full lifecycle compatibility with Claude Code, Google Antigravity, Cursor, OpenAI Codex, Windsurf, Continue, Cline, and GitHub Copilot.
- **5 Curated Domain Skill Packs (14 Grade A Reference Skills):**
  - *Office Productivity Pack*: File organizer, CSV report generator, Excel comparison, structured notes formatter, markdown validator.
  - *Finance & ERP Pack*: Financial variance analyzer, invoice reconciliation.
  - *HR & Workforce Pack*: Attendance CSV validator, timesheet reconciliation.
  - *Project Management Pack*: RAID log validator, project status reporter.
  - *Developer & Security Pack*: Security config scanner, dependency manifest reviewer, test inventory analyzer.
- **Optional AI-Assisted Skill Creation:** Turn natural language prompts into tested skills (`skillfactory ai-create`) with AST safety interception and bounded test self-repair.
- **Beginner Guided Walkthrough:** Interactive step-by-step wizard (`skillfactory guide`) with pre-flight diagnostics and platform auto-detection.
- **Symlink Escape & Prompt Injection Defense:** Hardened against symlink escapes, path traversal, Zip-Slip, and 7 categories of prompt injection.

### Quick Start:

```bash
# Install via pip
pip install skillfactory

# Or clone and run directly (zero install required)
git clone https://github.com/imnashraf/skill-factory.git
cd skill-factory
python3 -m skillfactory
```

Documentation and guides: [Skill Factory GitHub Repository](https://github.com/imnashraf/skill-factory)
````

---

## 3. Community Announcement Drafts

### A. Hacker News ("Show HN")

**Title:** Show HN: Skill Factory – Local-first open-source ecosystem for AI agent skills

**Text:**

> Hi HN! We built Skill Factory because developing and sharing custom skills for AI coding assistants (like Claude Code, Cursor, Windsurf, and Google Antigravity) currently suffers from fragmented formats, unvalidated scripts, and manual copy-pasting.
>
> Skill Factory is a local-first, zero-dependency Python toolkit that standardizes the skill lifecycle:
>
> 1. **Scaffolding & Templates:** Generates clean SKILL.md specs, execution scripts, and unit tests.
> 2. **Validation & Quality:** Checks frontmatter schema, file integrity, and computes a 0–100 quality score across 5 dimensions.
> 3. **Security Auditing:** Static AST scanner checks for unsafe subprocess execution, arbitrary evals, and network calls before installation; defenses against Zip-Slip, symlink escapes, and prompt injections.
> 4. **Safe Installation & Rollback:** Manifest-tracked installation with SHA-256 checksums, collision guards, and instant rollback across 8 AI coding assistants.
> 5. **Curated Domain Packs:** 14 verified Grade A reference skills spanning Office Productivity, Finance & ERP, HR & Workforce, Project Management, and Security.
> 6. **Optional AI Creation:** Natural language skill generation via local Ollama or OpenAI-compatible endpoints with AST pre-execution safety screening and bounded repair.
>
> It requires zero external libraries (pure standard library) and makes zero external network calls.
>
> Repository: [https://github.com/imnashraf/skill-factory](https://github.com/imnashraf/skill-factory)
>
> We would love your feedback on the architecture, format standardization, and security model!

### B. Reddit (r/Python, r/LocalLLaMA, r/ClaudeAI, r/Cursor)

**Title:** Skill Factory — A local-first, zero-dependency tool to build, audit, and install AI assistant skills (Claude, Cursor, Windsurf, Antigravity, Copilot)

**Text:**

> Most AI coding assistants now support external skills, but authoring them is often ad-hoc and unverified.
>
> Skill Factory provides an open, structured ecosystem:
>
> - **Pure Python Standard Library:** Zero pip dependencies required at runtime.
> - **8 Assistant Integrations:** Native path resolution and lifecycle management for Claude Code, Cursor, Google Antigravity, OpenAI Codex, Windsurf, Continue, Cline, and GitHub Copilot.
> - **Curated Packs:** 14 Grade A reference skills (Excel diffing, attendance auditing, invoice reconciliation, RAID log validator, security scanner, dependency reviewer, etc.).
> - **Security by Default:** Static AST inspection, prompt injection defense, Zip-Slip protection, symlink escape defense, and manifest-backed atomic rollback.
> - **AI-Assisted Engine:** Translate natural-language descriptions into validated skills using your local Ollama or compatible LLM with AST sandbox guards.
>
> Repository: [https://github.com/imnashraf/skill-factory](https://github.com/imnashraf/skill-factory)
>
> Feedback and contributions welcome!

### C. LinkedIn & Developer Forums

**Text:**

> Excited to introduce **Skill Factory** v1.2.0—an open-source, local-first ecosystem for creating, testing, and managing AI agent skills across major coding assistants.
>
> Whether you use Claude Code, Cursor, Windsurf, Google Antigravity, Continue, Cline, or Copilot, Skill Factory standardizes how skills are scaffolded, evaluated, and securely installed.
>
> 🔹 100% Python Standard Library (zero runtime third-party dependencies)  
> 🔹 5 Curated Domain Packs (14 Grade A reference skills)  
> 🔹 Built-in AST safety scanner, secret detector, and prompt injection defense  
> 🔹 Optional AI-assisted skill generation using local models  
> 🔹 Manifest-backed installation with one-command rollback  
>
> Explore the project: [Skill Factory GitHub Repository](https://github.com/imnashraf/skill-factory)

---

## 4. AI Coding Assistant Compatibility Comparison (8 Platforms)

| Platform | Project Scope Folder | Global (User) Scope Folder | Verification Level & Activation Model |
| :--- | :--- | :--- | :--- |
| **Claude Code** | `.claude/skills/<name>/` | `~/.claude/skills/<name>/` | **Verified Autonomous Activation:** Host model matches prompt intent to `SKILL.md` description; also supports manual `/<skill-name>` command. |
| **Google Antigravity** | `.agents/skills/<name>/` | `~/.gemini/config/skills/` | **Verified Autonomous Activation:** Engine injects discovered skills into system prompt `<skills>` context; model autonomously reads `SKILL.md` when intent matches. |
| **Cursor** | `.agents/skills/<name>/`, `.cursor/skills/` | `~/.agents/skills/`, `~/.cursor/skills/` | **Verified Directory Discovery:** Discovered in workspace or global folder; invoked via manual slash command `/<skill-name>` or explicit `@` context inclusion. |
| **OpenAI Codex** | `.agents/skills/<name>/` | `~/.agents/skills/` | **Simulated CLI Integration:** Discovered in `.agents/skills/`; invoked via CLI syntax `$<skill-name>`; respects `agents/openai.yaml` metadata. |
| **Windsurf** | `.codeium/windsurf/skills/<name>/` | `~/.codeium/windsurf/skills/<name>/` | **Verified Directory Discovery:** Discovered in Codeium Cascade workspace configuration. |
| **Continue** | `.continue/prompts/<name>/` | `~/.continue/prompts/<name>/` | **Verified Prompt / Tool Folder:** Discovered in Continue prompt/custom commands directory. |
| **Cline** | `.cline/skills/<name>/` | `~/.cline/skills/<name>/` | **Verified Workspace Skill Path:** Discovered in project `.cline/` root directory. |
| **GitHub Copilot** | `.github/skills/<name>/` | `~/.config/github-copilot/skills/<name>/` | **Verified Repository Instruction Path:** Discovered in `.github/` repository directory. |

---

## 5. Zero-Telemetry Privacy-Respecting Adoption Measurement

Skill Factory operates under a strict **Zero-Telemetry Policy**. The tool does not contact remote servers, track IP addresses, or collect usage analytics.

Adoption is measured strictly through public, privacy-preserving indicators:

1. **Public GitHub Metrics:**
   - Star growth and fork frequency.
   - Release asset download counts via the public GitHub Releases API.
2. **Community Activity:**
   - Issues opened, answered, and closed.
   - Pull requests submitted and merged.
   - Community skill submissions via the `.github/ISSUE_TEMPLATE/skill_submission.yml` workflow.
3. **Distribution Metrics:**
   - Public PyPI download statistics (via PyPI stats / `pypistats`, aggregate numbers only, without user identifiers).
4. **Documentation Feedback:**
   - Questions and clarifications raised in GitHub Discussions or issues.

---

## 6. Pre-Launch Checklist

- [x] Repository README clearly communicates value proposition and limitations.
- [x] Beginner quick-start guide tested across macOS, Windows, and Linux.
- [x] All 14 reference skills validated and evaluated at Grade A (≥90/100).
- [x] Test suite passing with 100% green status across all supported Python versions.
- [x] No secrets, private credentials, or internal test files committed.
- [x] Security reporting policy documented in `SECURITY.md`.
- [x] Contribution workflow and Code of Conduct published.
- [x] GitHub issue and pull request templates configured.
- [ ] Maintainer authorization obtained before public announcement broadcasts.
