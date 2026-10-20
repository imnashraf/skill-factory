# Skill Factory — Phase 15 Execution Plan

**Document Version:** 1.0.0  
**Baseline Version:** `v1.1.0` (Commit `bb065f0`)  
**Status:** In Execution  

---

## 1. Phased Execution Roadmap

The execution proceeds through 8 sequential stages, with full regression validation at every boundary:

```text
Stage 1: Audit & Baseline
   │
   ▼
Stage 2: Distribution & Onboarding (Workstreams A & B)
   │
   ▼
Stage 3: Domain Catalog & Reference Packs (Workstream D)
   │
   ▼
Stage 4: AI-Assisted Skill Creation (Workstream E)
   │
   ▼
Stage 5: Platform & Ecosystem Expansion (Workstream F)
   │
   ▼
Stage 6: Security & Quality Hardening (Workstream G)
   │
   ▼
Stage 7: Adoption & Community Readiness (Workstreams C & H)
   │
   ▼
Stage 8: Final Integration, Packaging & Release Candidate
```

---

## 2. Stage-by-Stage Implementation Tasks

### Stage 1: Audit & Baseline

- [x] Run baseline test suite (133 tests passed).
- [x] Run baseline security & multiagent test suites (all passed).
- [x] Create dedicated branch `feat/phase-15-master-execution`.
- [x] Audit PyPI registry availability (`skill-factory` vs `skillfactory`).
- [x] Establish Phase 15 documentation hub (`docs/phase15/*`).

### Stage 2: Distribution & Onboarding (Workstreams A & B)

- [ ] Update `pyproject.toml` with dual console scripts (`skillfactory`, `skill-factory`), enhanced classifiers, and package data.
- [ ] Implement GitHub Actions PyPI Trusted Publishing workflow (`.github/workflows/pypi-publish.yml`).
- [ ] Implement `skillfactory.guide` interactive onboarding module and `skillfactory guide` CLI command.
- [ ] Enhance `skillfactory doctor` with platform-specific actionable remediations and environment guidance.
- [ ] Test local packaging (`python -m build`), sdist, wheel, and clean virtualenv installation.
- [ ] Verify offline installation behavior.

### Stage 3: Domain Catalog & Reference Packs (Workstream D)

- [ ] Define 3-tier domain taxonomy schema (Personal, Professional, Developer/Agent).
- [ ] Implement `skillfactory.pack` subsystem (`skillfactory pack list`, `install`, `verify`, `uninstall`).
- [ ] Deliver curated domain reference skills:
  - Office Productivity: `structured-notes-formatter` (joining `file-organizer`, `csv-to-report`, `excel-comparison`, `markdown-doc-validator`).
  - Finance & ERP: `financial-variance-analyzer`, `invoice-reconciliation`.
  - HR & Workforce: `attendance-csv-validator`, `timesheet-reconciliation`.
  - Project Management: `raid-log-validator`, `project-status-reporter`.
  - Developer & Security: `dependency-manifest-reviewer`, `test-inventory-analyzer`.
- [ ] Provide synthetic, non-sensitive fixtures for each reference skill.
- [ ] Update `skillfactory/data/catalog.json` with domain taxonomy, pack metadata, and quality scores.

### Stage 4: AI-Assisted Creation (Workstream E)

- [ ] Design provider-neutral interface in `skillfactory.ai.provider.AIProvider`.
- [ ] Implement `OllamaProvider` (local-first, zero cost, no external API keys).
- [ ] Implement `OpenAICompatibleProvider` (vLLM, LM Studio, LocalAI).
- [ ] Implement `MockAIProvider` (deterministic, offline-first for tests and CI).
- [ ] Implement `skillfactory.ai.engine`:
  - Requirement interpreter and `SkillSpec` builder.
  - Scaffolding and script generator.
  - Pre-execution AST safety scan and prompt injection shield.
  - Subprocess execution in isolated temporary directory (10s timeout).
  - Bounded self-repair loop (up to 3 retries).
  - Draft quarantine and explicit human installation confirmation.
- [ ] Implement `skillfactory ai-create` CLI command with interactive or spec-driven execution.

### Stage 5: Platform Expansion (Workstream F)

- [ ] Extend `skillfactory/data/platforms.json` with verified platform definitions:
  - Windsurf (Codeium)
  - Continue (Continue.dev)
  - Cline
  - GitHub Copilot
- [ ] Update platform detection rules in `skillfactory/compat/detect.py`.
- [ ] Update resolution rules in `skillfactory/compat/resolve.py`.
- [ ] Add unit and lifecycle tests for all new platforms.

### Stage 6: Security & Quality Hardening (Workstream G)

- [ ] Extend AST safety scanner rules (block dangerous imports, dynamic exec, shell calls).
- [ ] Harden prompt injection regex patterns in `skillfactory/scanner.py`.
- [ ] Validate symlink target safety in `skillfactory/installer.py`.
- [ ] Add adversarial security test suite covering all 14 threat vectors.

### Stage 7: Adoption & Community Readiness (Workstreams C & H)

- [ ] Revamp `README.md` with complete Phase 15 features, visual architecture, and honest capability boundaries.
- [ ] Create production GitHub issue templates (`.github/ISSUE_TEMPLATE/*`) and pull request template (`.github/pull_request_template.md`).
- [ ] Prepare public launch materials (Show HN, Reddit, LinkedIn, Developer Forums) in `docs/launchPreparation.md`.
- [ ] Document zero-telemetry adoption measurement framework.
- [ ] Update `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md`.

### Stage 8: Final Integration, Packaging & Release Candidate

- [ ] Run full unit test suite (>150 tests).
- [ ] Run multiagent platform lifecycle validation.
- [ ] Run security threat model test suite.
- [ ] Execute clean package build and isolated virtualenv installation test.
- [ ] Compile comprehensive Phase 15 final verification report.
