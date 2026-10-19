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
| `FR16-01` | 16 | Usability | Zero raw stack traces, OS-specific path guidance, friendly error remediation | Must | PENDING | Implementation in Workstream 16A |
| `FR16-02` | 16 | AI Creation | Structured natural-language requirements interpreter (intent, I/O, rules, tests) | Must | PENDING | Implementation in Workstream 16B |
| `FR16-03` | 16 | AI Creation | Explicit Assumption Register for ambiguous business requirements | Should | PENDING | Implementation in Workstream 16B |
| `FR16-04` | 16 | Quality | Automated behavioral test generation from acceptance criteria / spec | Must | PENDING | Implementation in Workstream 16C |
| `FR16-05` | 16 | AI Creation | Bounded code generation & self-repair loop with stderr feedback (max 3 retries) | Must | PENDING | Implementation in Workstream 16C |
| `FR16-06` | 16 | Usability | Deterministic non-AI specification & scaffolding fallback when model unavailable | Must | PENDING | Implementation in Workstream 16C |
| `FR16-07` | 16 | Quality | Functional correctness checking against boundary test fixtures; independent scoring | Must | PENDING | Implementation in Workstream 16D |
| `FR16-08` | 16 | Validation | Simulated beginner journey evaluation measuring steps, error recovery, and latency | Should | PENDING | Implementation in Workstream 16E |
| `FR17-01` | 17 | Ecosystem | Extensible 3-tier domain taxonomy with dynamic domain registration | Must | PENDING | Implementation in Workstream 17A |
| `FR17-02` | 17 | Discovery | Multi-attribute offline catalog search (keyword, domain, category, platform, grade) | Must | PENDING | Implementation in Workstream 17B |
| `FR17-03` | 17 | Ecosystem | Curated skill pack preview, dependency resolution, and atomic rollback | Must | PENDING | Implementation in Workstream 17C |
| `FR17-04` | 17 | Community | Automated contribution validation script & pull request screening workflow | Must | PENDING | Implementation in Workstream 17D |
| `FR17-05` | 17 | Security | Strict security quarantine: untrusted community submissions never executed automatically | Must | PENDING | Implementation in Workstream 17D |
| `FR17-06` | 17 | Discovery | Standalone offline Markdown catalog generator (`docs/SKILL_CATALOG.md`) | Should | PENDING | Implementation in Workstream 17E |
| `FR18-01` | 18 | Architecture | Full codebase architecture review: dead code removal, 100% stdlib purity | Must | PENDING | Implementation in Workstream 18A |
| `FR18-02` | 18 | Security | Comprehensive 16-vector threat model audit, mitigations, and residual risk registry | Must | PENDING | Implementation in Workstream 18B |
| `FR18-03` | 18 | Compatibility| Cross-platform verification (macOS, Linux, Windows; Py 3.9–3.13) | Must | PENDING | Implementation in Workstream 18C |
| `FR18-04` | 18 | Performance | Production performance benchmark harness validating sub-10ms budgets | Must | PENDING | Implementation in Workstream 18D |
| `FR18-05` | 18 | Documentation| Complete documentation suite: guides, API reference, security, maintenance policy | Must | PENDING | Implementation in Workstream 18E |
| `FR18-06` | 18 | Release | Final production release candidate (clean install test, checksums, release notes) | Must | PENDING | Implementation in Workstream 18F |
| `FR18-07` | 18 | Governance | Long-term maintenance readiness: bug triage, security disclosure, deprecation policy | Must | PENDING | Implementation in Workstream 18G |

---

## 2. Requirement Status Categories

- **VERIFIED**: Independently verified against working code, automated test evidence, and execution outputs.
- **PENDING**: Scheduled for execution in the current master plan.
- **EXPERIMENTAL / DEFERRED**: Identified as non-essential enhancement or held pending external capabilities.
- **BLOCKED**: Requires external maintainer authorization (e.g. PyPI credentials, public release tagging).
