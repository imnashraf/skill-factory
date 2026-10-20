# Skill Factory — Phase 15 Architecture

**Document Version:** 1.0.0  
**Baseline Version:** `v1.1.0` (Commit `bb065f0`)  
**Status:** Approved Architecture  

---

## 1. System Architecture Overview

Skill Factory Phase 15 extends the core engine into a cohesive, modular open-source ecosystem:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             SKILL FACTORY CLI                               │
│  new | validate | test | eval | scan | doctor | install | pack | ai | guide │
└───────────────────────┬─────────────────────────────┬───────────────────────┘
                        │                             │
       ┌────────────────┴───────────────┐  ┌──────────┴────────────────┐
       ▼                                ▼  ▼                           ▼
┌──────────────┐                 ┌──────────────┐               ┌──────────────┐
│  AI ASSISTED │                 │ DOMAIN SKILL │               │ PLATFORM     │
│   CREATION   │                 │  ECOSYSTEM   │               │ ADAPTERS     │
│ (Provider    │                 │ (3-Tier Tax- │               │ (Claude, AGY,│
│  Neutral,    │                 │  onomy, Pack │               │  Cursor,     │
│  Sandbox,    │                 │  Installer,  │               │  Codex,      │
│  Repair)     │                 │  Ref Skills) │               │  Windsurf,   │
│              │                 │              │               │  Continue,   │
│              │                 │              │               │  Cline,      │
│              │                 │              │               │  Copilot)    │
└──────┬───────┘                 └──────┬───────┘               └──────┬───────┘
       │                                │                              │
       └────────────────┬───────────────┴──────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SECURITY, QUALITY & INTEGRITY LAYER                     │
│  AST Safety Scanner │ Secrets Detector │ Prompt Injection Shield            │
│  SHA-256 Manifest   │ Zip-Slip Guard   │ Unmanaged Overwrite Protection     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Workstream Architectural Details

### 2.1 Distribution Architecture (Workstream A)

- **Entrypoints:** Dual console scripts `skillfactory` and `skill-factory` mapped to `skillfactory.cli:main` in `pyproject.toml`.
- **Packaging:** Standard PEP 517 / PEP 621 build using `setuptools.build_meta`. Includes all package data (`skillfactory/data/*.json`, templates).
- **Trusted Publishing:** GitHub Actions workflow utilizing OpenID Connect (`id-token: write`) to eliminate long-lived PyPI API tokens.

### 2.2 Beginner Experience & Guided Onboarding (Workstream B)

- **Module:** `skillfactory.guide`
- **Workflow:**
  1. **Diagnostics:** Pre-flight checks on Python version, disk writability, installed AI coding assistants.
  2. **Assistant Selection:** Automatic detection with guided single-choice fallback.
  3. **Skill Purpose:** Natural language prompt or interactive question-and-answer flow.
  4. **Scaffolding:** Immediate generation with deterministic validation.
  5. **Next Steps:** Actionable, formatted checklist explaining how to activate and test the skill.

### 2.3 Domain Skill Ecosystem (Workstream D)

- **Taxonomy Schema:**
  - `personal`: Productivity, organization, education, expense tracking.
  - `professional`: Finance, HR, project management, ERP operations.
  - `developer`: Code quality, security, CI/CD, testing, release automation.
- **Pack Management Subsystem (`skillfactory.pack`):**
  - `skillfactory pack list`: Browse available curated packs and their skills.
  - `skillfactory pack install <pack_name>`: Atomically install all skills in a pack into the target assistant with collision checks and rollback.
  - `skillfactory pack verify <pack_name>`: Run validation, safety scans, and tests across all skills in a pack.
  - `skillfactory pack uninstall <pack_name>`: Cleanly remove installed pack skills while preserving user files.

### 2.4 AI-Assisted Skill Development Engine (Workstream E)

- **Module Structure (`skillfactory.ai`):**
  - `provider.py`: Abstract base class `AIProvider` defining:
    - `generate_code(spec: SkillSpec, prompt: str) -> Dict[str, str]`
    - `repair_code(spec: SkillSpec, code: Dict[str, str], errors: str) -> Dict[str, str]`
  - `ollama.py`: `OllamaProvider` connecting to local Ollama endpoints (e.g. `http://localhost:11434/api/generate`) with zero cloud dependencies.
  - `openai_compat.py`: `OpenAICompatibleProvider` connecting to local LLMs (vLLM, LM Studio, LocalAI) or user-configured endpoints.
  - `mock_provider.py`: Deterministic `MockAIProvider` for test execution, offline verification, and CI pipelines.
  - `engine.py`: Orchestrator coordinating:
    1. Requirement analysis & `SkillSpec` derivation.
    2. Code & test scaffolding generation.
    3. AST safety scanning & prompt injection analysis before execution.
    4. Subprocess execution in isolated temporary directory with a 10s timeout.
    5. Bounded self-repair loop (up to 3 iterations) on test failure.
    6. Quarantine and human confirmation prompt before installation.

### 2.5 Multi-Platform Compatibility Expansion (Workstream F)

- **Platform Database (`skillfactory/data/platforms.json`):**
  - **Claude Code**: `.claude/skills/`, user `~/.claude/skills/`.
  - **Google Antigravity**: `.agents/skills/`, user `~/.gemini/config/skills/`.
  - **Cursor**: `.agents/skills/`, `.cursor/skills/`.
  - **OpenAI Codex**: `.agents/skills/`.
  - **Windsurf**: Project `.codeium/windsurf/memories` and `.windsurfrules`.
  - **Continue**: Project `.continue/prompts/<skill-name>.prompt`.
  - **Cline**: Project `.clinerules` and `.cline/skills/`.
  - **GitHub Copilot**: Project `.github/copilot-instructions.md`.
- **Resolution Engine (`skillfactory.compat.resolve`):**
  - Resolves target directory based on platform ID and scope (project vs user).
  - Handles platform-specific formatting and frontmatter rules.

### 2.6 Security & Trust Layer (Workstream G)

- **Threat Matrix Coverage (14 Vectors):**
  - `TV-01`: Zip-Slip path traversal during archive import.
  - `TV-02`: Symlink escape outside designated project/user skill root.
  - `TV-03`: Prompt injection payloads in skill markdown / descriptions.
  - `TV-04`: Dynamic Python code execution (`eval`, `exec`, `__import__`).
  - `TV-05`: Shell injection via `subprocess.Popen(..., shell=True)` or `os.system`.
  - `TV-06`: Hardcoded API secrets and private cryptographic keys.
  - `TV-07`: Unmanaged file overwrite without `--force`.
  - `TV-08`: Malicious dependencies in untrusted imports.
  - `TV-09`: Infinite test loops / denial of service (10s timeout guard).
  - `TV-10`: Corrupted archive / tampered manifest (SHA-256 validation).
  - `TV-11`: Unchecked AI-generated code execution.
  - `TV-12`: Unsanitized CLI arguments and file paths.
  - `TV-13`: Privilege escalation via platform config tampering.
  - `TV-14`: Accidental telemetry leakage (100% offline, zero network requests).
