# Skill Factory — Phase 15 Decision Log

**Document Version:** 1.0.0  
**Baseline Version:** `v1.1.0` (Commit `bb065f0`)  
**Status:** Approved & Implemented  

---

## Decision D15-01: PyPI Package Namespace & Distribution Strategy

### Context

Workstream A requires preparing Skill Factory for simple, secure PyPI distribution via `pip install skill-factory`. In accordance with prompt instructions ("First verify whether the intended distribution name is available and whether existing ownership or namespace conflicts exist. Do not assume the package name is available."), an empirical live check of the PyPI registry API (`https://pypi.org/pypi/<name>/json`) was executed on 2026-10-19.

### Findings

1. `https://pypi.org/pypi/skill-factory/json`: **EXISTS (HTTP 200)**.
   - Owner/Author: François Chastel (`francois@chastel.co`).
   - Repository: `https://github.com/FrancoisChastel/skill-factory`.
   - Summary: "Scientifically optimize portable agent skills (SKILL.md) across harnesses using pluggable optimizers...".
   - Latest Version: 0.2.0.
2. `https://pypi.org/pypi/skillfactory/json`: **NOT FOUND (HTTP 404)**.
   - Package name `skillfactory` (unhyphenated) is not currently registered.
3. PyPI Normalization & Conflict Rules:
   - PEP 503 normalizes names with `_`, `-`, and `.` to `-`.
   - Because `skill-factory` already exists, any upload named `skill_factory` or `skill-factory` is blocked.
   - `skillfactory` does not have a hyphen, but PyPI Warehouse may enforce name-similarity / typosquatting safeguards when creating a new project.

### Decision

1. In `pyproject.toml`, retain `name = "skillfactory"`.
2. Provide two console script entry points in `[project.scripts]`:

   ```toml
   [project.scripts]
   skillfactory = "skillfactory.cli:main"
   skill-factory = "skillfactory.cli:main"
   ```

   This ensures that once installed, users can type either `skillfactory` or `skill-factory` interchangeably.
3. In documentation and onboarding guides, clearly instruct users:

   ```bash
   pip install skillfactory
   ```

   Explicitly warn users that running `pip install skill-factory` installs an unrelated third-party package (`francois@chastel.co`).
4. Document the exact steps required for human maintainers if namespace transfer or disambiguation (`skillfactory-cli`) is pursued.

---

## Decision D15-02: Zero-Telemetry and Local-First Policy

### Context

Workstream C requires proposing privacy-respecting ways to evaluate public adoption without introducing invasive telemetry or collecting sensitive user metrics.

### Decision

1. Skill Factory shall remain 100% local-first and zero-telemetry. No analytics pings, no network beacons, no tracking pixels, and no phone-home mechanisms.
2. Adoption measurement is based entirely on public, voluntary signals:
   - GitHub stars, watchers, and forks.
   - GitHub Releases asset download counts (via GitHub API).
   - Public issue reports and community pull requests.
   - Manual community surveys and feedback forms.

---

## Decision D15-03: Provider-Neutral AI Skill Generation Architecture

### Context

Workstream E requires designing an optional AI-assisted skill development workflow that can turn natural language requirements into functioning skills without locking users into expensive paid APIs or cloud dependencies.

### Decision

1. Implement a pluggable, provider-neutral architecture in `skillfactory.ai`:
   - `AIProvider`: Abstract base class with `generate_code(spec, prompt)` and `repair_code(spec, code, test_failures)`.
   - `OllamaProvider`: Default local inference provider connecting to local Ollama endpoints (e.g. `http://localhost:11434`), requiring zero cloud credentials and zero cost.
   - `OpenAICompatibleProvider`: Compatible with vLLM, LM Studio, LocalAI, or custom endpoints.
   - `MockAIProvider`: Fully deterministic offline provider for unit testing, CI builds, and developer environments.
2. **Safety Sandbox Rule:** All AI-generated code must pass the AST safety scanner (`skillfactory.scanner`) and secrets detector before execution. Code with dangerous calls (eval, exec, shell=True) is automatically rejected.
3. **Execution Isolation:** Generated test execution occurs in an isolated subprocess with a strict 10-second timeout, memory bounds, and directory isolation.
4. **Human-in-the-Loop:** Even if all automated tests pass, the skill is quarantined in `.skillfactory/drafts/` until the user explicitly approves installation via CLI prompt or `--yes`.

---

## Decision D15-04: Structured 3-Tier Domain Skill Taxonomy

### Context

Workstream D requires establishing a clear taxonomy across three domains: Personal, Professional, and Developer/Agent, and delivering practical, deterministic reference packs.

### Decision

1. Define a standardized 3-tier taxonomy schema:
   - `personal`: File management, personal productivity, learning, expense reporting, household.
   - `professional`: Finance/ERP, HR/workforce, procurement, project management, operations.
   - `developer`: Software engineering, testing, security, DevOps, release management.
2. Implement 5 curated domain packs with deterministic reference skills:
   - **Office Productivity Pack**: `file-organizer`, `csv-to-report`, `markdown-doc-validator`, `excel-comparison`, `structured-notes-formatter`.
   - **Finance & ERP Pack**: `financial-variance-analyzer`, `invoice-reconciliation`, `po-matching-checker`.
   - **HR & Workforce Pack**: `attendance-csv-validator`, `timesheet-reconciliation`, `leave-data-checker`.
   - **Project Management Pack**: `raid-log-validator`, `project-status-reporter`, `milestone-variance-analyzer`.
   - **Developer & Security Pack**: `security-config-scanner`, `dependency-manifest-reviewer`, `test-inventory-analyzer`.
3. Provide the `skillfactory pack` CLI command suite (`pack list`, `pack install`, `pack verify`, `pack uninstall`).

---

## Decision D15-05: Platform Adapter Expansion Standards

### Context

Workstream F requires evaluating and integrating additional AI coding assistants while avoiding fragile or fake integrations.

### Decision

1. For each platform added to `skillfactory/data/platforms.json`:
   - Must have official documentation validating directory conventions and file formats.
   - Must support deterministic project-level or user-level discovery.
2. Verified platform additions:
   - **Windsurf** (Codeium): `.codeium/windsurf/memories` and `.windsurfrules`.
   - **Continue** (Continue.dev): `.continue/prompts/` slash-command prompts.
   - **Cline**: `.clinerules` project rules and `.cline/skills/` skill trees.
   - **GitHub Copilot**: `.github/copilot-instructions.md` workspace instructions.
3. Preserve full backward compatibility and lifecycle stages for existing primary platforms: Claude Code, Cursor, Codex, and Google Antigravity.

---

## Decision D15-06: PyPI Trusted Publishing (OIDC) Workflow

### Context

Workstream A requires configuring PyPI publishing using the recommended GitHub Actions OIDC Trusted Publishing standard rather than long-lived API tokens.

### Decision

1. Create `.github/workflows/pypi-publish.yml` with:
   - `permissions: id-token: write`
   - Least-privilege authorization scoped strictly to release tags or manual workflow dispatch.
   - PyPI official action: `pypa/gh-action-pypi-publish@release/v1`.
2. Do not embed any static credentials, tokens, or passwords in repository files.
