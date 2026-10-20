# Master Requirements & Traceability Matrix (Phases 15–18)

This document establishes the formal requirements, priorities, acceptance criteria, and implementation status for the final major development program of Skill Factory (Phases 15 through 18).

---

## 1. Traceability Matrix

| Req ID | Phase | Category | Description | Priority | Status | Verification Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FR15-01` | 15 | Packaging | Dual CLI entrypoints (`skillfactory` & `skill-factory`) | Must | VERIFIED | `pyproject.toml`, clean venv test |
| `FR15-02` | 15 | Distribution | PyPI distribution readiness & OIDC Trusted Publishing | Must | VERIFIED | `.github/workflows/pypi-publish.yml`, dist wheel |
| `FR15-03` | 15 | Onboarding | Interactive guided walkthrough wizard (`skillfactory guide`) | Must | VERIFIED | `skillfactory/guide.py`, CLI tests |
| `FR15-04` | 15 | Ecosystem | 3-tier taxonomy schema & 5 curated domain skill packs | Must | VERIFIED | `skillfactory/pack.py`, `packs.json` |
| `FR15-05` | 15 | Reference | 14 reference skills scoring Grade A (≥90/100) | Must | VERIFIED | `generated-skills/`, evaluation runner |
| `FR15-06` | 15 | AI Creation | Provider-neutral AI creation engine with AST quarantine | Must | VERIFIED | `skillfactory/ai/`, 14 engine tests |
| `FR15-07` | 15 | Platforms | 8 AI coding assistant integrations verified across 6 lifecycle stages | Must | VERIFIED | `tests/run_multiagent_validation.py` |
| `FR15-08` | 15 | Security | Symlink escape defense and prompt injection rules INJ005–INJ007 | Must | VERIFIED | `tests/run_security_validation.py` |
| `FR16-01` | 16 | Usability | Zero raw stack traces, OS-specific path guidance, friendly error remediation | Must | VERIFIED | `skillfactory/guide.py`, `tests/test_beginner_experience.py` |
| `FR16-02` | 16 | AI Creation | Structured natural-language requirements interpreter (intent, I/O, rules, tests) | Must | VERIFIED | `skillfactory/ai/requirements.py`, `tests/test_requirements.py` |
| `FR16-03` | 16 | AI Creation | Explicit Assumption Register for ambiguous business requirements | Should | VERIFIED | `AssumptionRegister` in `requirements.py`, markdown export |
| `FR16-04` | 16 | Quality | Automated behavioral test generation from acceptance criteria / spec | Must | VERIFIED | `skillfactory/ai/test_gen.py`, `tests/test_test_gen.py` |
| `FR16-05` | 16 | AI Creation | Bounded code generation & self-repair loop with stderr feedback (max 3 retries) | Must | VERIFIED | `AIAssistedEngine.build_skill()`, `tests/test_ai_engine.py` |
| `FR16-06` | 16 | Usability | Deterministic non-AI specification & scaffolding fallback when model unavailable | Must | VERIFIED | `generate_non_ai_implementation()`, `tests/test_evaluator.py` |
| `FR16-07` | 16 | Quality | Functional correctness checking against boundary test fixtures; independent scoring | Must | VERIFIED | `audit_functional_correctness()`, `tests/test_evaluator.py` |
| `FR16-08` | 16 | Validation | Simulated beginner journey evaluation measuring steps, error recovery, and latency | Should | VERIFIED | `tests/test_beginner_experience.py` (Simulated) |
| `FR17-01` | 17 | Ecosystem | Extensible 3-tier domain taxonomy with dynamic domain registration | Must | VERIFIED | `skillfactory/library.py`, `tests/test_library_search.py` |
| `FR17-02` | 17 | Discovery | Multi-attribute offline catalog search (keyword, domain, category, platform, grade) | Must | VERIFIED | `search_catalog()`, `tests/test_library_search.py` (<10ms) |
| `FR17-03` | 17 | Ecosystem | Curated skill pack preview, dependency resolution, and atomic rollback | Must | VERIFIED | `preview_pack()`, `skillfactory/pack.py`, `tests/test_pack_preview.py` |
| `FR17-04` | 17 | Community | Automated contribution validation script & pull request screening workflow | Must | VERIFIED | `scripts/validate_submission.py`, `tests/test_submission_screening.py` |
| `FR17-05` | 17 | Security | Strict security quarantine: untrusted community submissions never executed automatically | Must | VERIFIED | Quarantine barrier in `scripts/validate_submission.py` |
| `FR17-06` | 17 | Discovery | Standalone offline Markdown catalog generator (`docs/SKILL_CATALOG.md`) | Should | VERIFIED | `docs/SKILL_CATALOG.md` (14 skills, 5 packs, 31 domains) |
| `FR18-01` | 18 | Architecture | Full codebase architecture review: dead code removal, 100% stdlib purity | Must | VERIFIED | AST import audit (0 third-party imports), `architectureDecisions.md` |
| `FR18-02` | 18 | Security | Comprehensive 16-vector threat model audit, mitigations, and residual risk registry | Must | VERIFIED | `securityFindings.md`, `riskRegister.md`, `run_security_validation.py` |
| `FR18-03` | 18 | Compatibility | Cross-platform verification (macOS, Linux, Windows; Py 3.9–3.14) | Must | VERIFIED | `compatibilityEvidence.md`, `run_multiagent_validation.py` |
| `FR18-04` | 18 | Performance | Production performance benchmark harness validating sub-10ms budgets | Must | VERIFIED | `scripts/run_benchmarks.py` (search 0.02ms, startup 3.05ms) |
| `FR18-05` | 18 | Documentation | Complete documentation suite: guides, API reference, security, maintenance policy | Must | VERIFIED | `README.md`, `SKILL_CATALOG.md`, `CLI_REFERENCE.md`, `maintenancePolicy.md` |
| `FR18-06` | 18 | Release | Final production release candidate (clean install test, checksums, release notes) | Must | VERIFIED | `dist/`, clean venv test `/tmp/sf_release_verify`, `releaseReadiness.md` |
| `FR18-07` | 18 | Governance | Long-term maintenance readiness: bug triage, security disclosure, deprecation policy | Must | VERIFIED | `docs/final-development/maintenancePolicy.md` |

---

## 2. Requirement Status Categories

- **VERIFIED**: Independently verified against working code, automated test evidence, and execution outputs.
- **PENDING**: Scheduled for execution in the current master plan.
- **EXPERIMENTAL / DEFERRED**: Identified as non-essential enhancement or held pending external capabilities.
- **BLOCKED**: Requires external maintainer authorization (e.g. PyPI credentials, public release tagging).
