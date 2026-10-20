# Project Risk Register & Mitigation Strategy

This document establishes the operational, technical, security, and maintenance risk register for the Skill Factory platform.

---

## 1. Risk Matrix

| Risk ID | Category | Description | Likelihood | Impact | Severity | Mitigation Strategy | Owner | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `RSK-01` | Security | Untrusted community PR executes malicious payload in CI | Low | Critical | **High** | Strict quarantine barrier: `validate_submission.py` forbids automated subprocess execution on unreviewed PRs. | Security Lead | **MITIGATED** |
| `RSK-02` | Distribution | PyPI package name collision or namespace takeover | Low | High | **Medium** | Claimed PyPI identifier `skillfactory` with dual entry points configured in `pyproject.toml`. | Release Lead | **MITIGATED** |
| `RSK-03` | Supply Chain | Stolen long-lived PyPI API token | Very Low | Critical | **Medium** | Configured tokenless GitHub Actions OIDC Trusted Publishing with restricted environment permissions. | DevOps Lead | **MITIGATED** |
| `RSK-04` | Architecture | Runtime dependency conflicts or broken upstream packages | Very Low | High | **Low** | 100% Python Standard Library commitment (zero external runtime dependencies). | Architect | **ELIMINATED** |
| `RSK-05` | Quality | AI model hallucinating passing grades (self-grading bias) | Medium | High | **High** | Decoupled functional correctness evaluator running independent standard library tests. | QA Lead | **MITIGATED** |
| `RSK-06` | Data Loss | Batch pack installation overwrites existing user skill | Low | High | **Medium** | Pre-installation preview with collision detection; refuse unmanaged overwrites. | Software Lead | **MITIGATED** |
| `RSK-07` | Portability | Path separator failures on Windows (`\` vs `/`) | Low | Medium | **Low** | Use `pathlib.Path` across all modules; CI test matrix across macOS, Ubuntu, Windows. | QA Lead | **MITIGATED** |
| `RSK-08` | Adoption | Beginners overwhelmed by technical prerequisites | Medium | Medium | **Medium** | Guided wizard (`skillfactory guide`), OS-specific path guidance, zero raw stack traces. | UX Lead | **MITIGATED** |

---

## 2. Review & Governance Schedule

- **Monthly**: Review dependency-free standard library compatibility against new Python releases.
- **Quarterly**: Review adversarial prompt injection heuristics (`INJ001`–`INJ007`) against emerging LLM jailbreak vectors.
- **Per Release**: Verify OIDC workflows, test matrix, and release integrity checksums.
