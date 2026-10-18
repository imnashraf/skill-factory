# Non-Functional Requirements

Each NFR has a **measurable** target and a verification method. Parent product requirements in brackets.

| ID | Category | Requirement | Target / measure | Verified by | Phase |
|---|---|---|---|---|---|
| NFR-01 | Cost [PR-01] | No mandatory paid service, API key, or account. | Full test suite and quickstart pass with network disabled and no credentials. | CI job with no network for tests (`unshare`/no secrets); review checklist | 1+ |
| NFR-02 | Dependencies [PR-13] | Runtime uses Python standard library only. | 0 third-party runtime imports; checked by an import-allowlist test. | `tests/test_no_third_party_imports.py` | 1 |
| NFR-03 | Python support [PR-17] | Minimum Python version per D-03 (proposed 3.9) to latest stable. | CI matrix covers minimum and latest; startup check exits code 3 with a friendly message below minimum. | CI matrix | 1 |
| NFR-04 | OS portability [PR-07] | Works on macOS, Windows, Linux. | CI matrix on `ubuntu-latest`, `macos-latest`, `windows-latest`; all tests pass. | CI | 1 |
| NFR-05 | Paths | All paths via `pathlib`; no hardcoded `/` or `\`; home via `Path.home()`; handles spaces and non-ASCII characters in paths. | Edge-case tests EC-10..EC-14 pass on all 3 OSes. | Tests | 1 |
| NFR-06 | Offline [PR-02] | No network call in any command except explicit `fetch`/remote-index commands. | Test that patches `socket.socket` to raise; all offline commands pass. | `tests/test_offline.py` | 1 |
| NFR-07 | Determinism | Same input → same output. | Golden-file tests compare generated output byte-for-byte (ignoring manifest timestamps). | Golden tests | 1 |
| NFR-08 | Performance | Generate a skill in < 2 s; validate in < 1 s; full self-test suite < 60 s per CI job. | Timed in CI. | CI | 1, 5 |
| NFR-09 | Reliability [PR-21] | No partial state after any failure (generate, install, update, uninstall). | Fault-injection tests (simulated write failure mid-operation) leave the filesystem unchanged. | Tests | 1, 4 |
| NFR-10 | Safety [PR-09] | No destructive operation without explicit confirmation or `--yes`; `--dry-run` everywhere that writes. | Tests assert prompts; review checklist. | Tests | 1, 4 |
| NFR-11 | Privacy [PR-18] | No telemetry, analytics, or crash reporting. | Static check: no network modules imported outside the explicit remote-index module. | Test | 1 |
| NFR-12 | Accessibility [PR-19] | Plain text output; meaning never by color alone; `NO_COLOR` honoured; output readable at 80 columns; interactive prompts accept typed answers (no arrow-key-only menus). | Snapshot tests of output; manual screen-reader check before v1.0 (VoiceOver + NVDA). | Tests + manual | 1, 7 |
| NFR-13 | Usability [PR-08] | A first-time user completes "create + validate + install" by following the quickstart. | ≥ 4 of 5 beginner testers succeed in ≤ 10 minutes without help (Phase 7 usability study). | Usability test | 7 |
| NFR-14 | Maintainability | Code is modular (see architecture), typed with annotations, documented; each module has unit tests. | Statement coverage ≥ 85% (stdlib `trace` or optional dev-only `coverage`). | CI report | 1+ |
| NFR-15 | Compatibility [PR-20] | No breaking changes to public CLI within a major version. | Compatibility tests for `scripts/create_skill.py` remain green. | Tests | All |
| NFR-16 | Documentation | Docs synchronised with code. | CI check: every CLI command has a docs entry; every FR ID in traceability. | CI script | 1+ |
| NFR-17 | Encoding | UTF-8 everywhere, explicitly specified on every file open; LF line endings for generated files. | Tests on Windows runner. | Tests | 1 |
| NFR-18 | Size | Installed skill footprint contains only allow-listed files (no tests of Skill Factory itself, no docs/ folder). | Install test checks file list. | Tests | 4 |
| NFR-19 | Supply chain | GitHub Actions pinned to full commit SHAs; minimal `permissions`; Dependabot for Actions only. | CI lint step. | CI | 8 |
