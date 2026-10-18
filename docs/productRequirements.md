# Product Requirements

Each product requirement (`PR-xx`) is broken down into functional (`FR-*`), non-functional (`NFR-*`) and security (`SEC-*`) requirements. Mapping: [requirementsTraceability.md](requirementsTraceability.md).

## Approved — from the product vision

| ID | Requirement | Phase(s) |
|---|---|---|
| PR-01 | Skill Factory is completely free and open-source (MIT). No mandatory paid APIs, subscriptions, or proprietary cloud services. | All |
| PR-02 | Local-first: every core feature (generate, validate, test, install, uninstall) works offline. | 1–5 |
| PR-03 | From a problem description, produce a reusable skill containing: `SKILL.md`, executable scripts where required, automated tests, `README.md`, examples and references, compatibility metadata, validation results, and installation instructions. | 1, 2, 5 |
| PR-04 | Natural-language generation may use the AI model already available in the user's host assistant. Without an AI model, an offline mode must remain functional using deterministic templates. | 2 |
| PR-05 | Generated skills follow the open Agent Skills specification (agentskills.io) so they are portable. | 1, 3 |
| PR-06 | Target AI platforms: Claude Code, Cursor, OpenAI Codex, Google Antigravity. | 3, 4 |
| PR-07 | Target operating systems: macOS, Windows, Linux. | All |
| PR-08 | Beginner-friendly experience. | 2, 7 |
| PR-09 | Safe by default: user approval for destructive operations; no hardcoded credentials; no mandatory telemetry. | All, 8 |
| PR-10 | Validate and test generated skills, including automated evaluation of quality, correctness, and safety. | 5 |
| PR-11 | Easy installation, updates, uninstall, and rollback. | 4 |
| PR-12 | Skill library and discovery; generated skills can be shared and published to GitHub. | 6 |
| PR-13 | Python standard-library solutions preferred; no unnecessary dependencies. | All |
| PR-14 | Public v1.0 release with documentation and automated quality checks (GitHub Actions). | 9 |

## Proposed — gaps identified in the planning review

These were not stated in the vision but are needed for a dependable, beginner-friendly, cross-platform product. **Each needs your approval** (accept / reject / modify).

| ID | Requirement | Why it is essential | Phase |
|---|---|---|---|
| PR-15 | **Honest compatibility claims.** Only claim support for a platform/OS/version that has been verified, and show the verification date. | The current README already promises this; platforms change paths frequently (Claude Code ships multiple releases per week). | 3, 9 |
| PR-16 | **Provenance and versioning of generated skills.** Each skill records its version, the Skill Factory version that generated it, the template used, and file hashes. | Needed for safe updates, rollback, and "is this file modified?" checks. | 1, 4 |
| PR-17 | **Python runtime policy.** A documented minimum Python version, tested in CI, plus a clear message if the user's Python is too old. | macOS ships Python 3.9 via Xcode tools; README says 3.9+ but CI tests only 3.11/3.13. See D-03. | 1 |
| PR-18 | **Privacy disclosure.** Skill Factory itself sends nothing anywhere; users are told that their host AI assistant may send their problem description to its provider. | Local-first promise must be accurate about the host AI. | 2, 7 |
| PR-19 | **Accessibility.** Plain-text, screen-reader-friendly CLI output; no information conveyed by color alone; `NO_COLOR` honoured. | Beginner-friendly must include users with disabilities. | 1, 7 |
| PR-20 | **Backward compatibility.** Existing commands (`scripts/create_skill.py`) and existing tests keep working; breaking changes only in major versions with a migration note. | Governance: "preserve all existing working code and tests". | All |
| PR-21 | **Recoverability.** No operation leaves a half-written skill or half-installed folder; every install/update can be undone. | Beginners cannot fix corrupted states by hand. | 1, 4 |
| PR-22 | **Licensing clarity for generated output.** Users choose the license of their generated skills; Skill Factory's own license does not force attribution into generated skills. | Legal obligation clarity; see LEG-xx in securityAndPrivacy.md and D-11. | 1, 6 |
| PR-23 | **Project governance files** (CONTRIBUTING, SECURITY policy, Code of Conduct, CHANGELOG). | Required for a credible public open-source release. | 8, 9 |
| PR-24 | **Data-driven platform knowledge.** Platform paths and rules live in a single data file that can be updated without code changes. | Platform behaviour changes faster than release cycles. | 3 |

## Explicitly out of scope for v1.0

See [problemStatement.md](problemStatement.md#non-goals-v10). Notably: no built-in AI API calls, no hosted service, no true sandbox, English-only UI.
