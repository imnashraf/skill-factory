# Automated Skill Evaluation & Quality Scoring

Skill Factory includes a built-in evaluation engine (`skillfactory eval <skill-dir>`) that scores any agent skill on an objective **0–100 scale**. 

This allows users, developers, and automated pipelines to instantly evaluate whether a skill is well-structured, safe, portable, and ready for deployment.

---

## 1. Multi-Dimensional Scoring Rubric (100 Points Total)

The evaluation engine assesses skills across five key dimensions:

```
+--------------------------------------------------------------------+
|                         Skill Quality Score (0–100)                |
+--------------------------------------------------------------------+
|  1. Spec Compliance & Structure   (25 pts)                         |
|  2. Cross-Platform Portability    (20 pts)                         |
|  3. Documentation & Ergonomics    (20 pts)                         |
|  4. Test Coverage & Execution     (20 pts)                         |
|  5. Code Safety & Secrets Scan    (15 pts)                         |
+--------------------------------------------------------------------+
```

---

### Dimension 1: Spec Compliance & Structure (25 Points) — `EV-01`
- **[5 pts] Mandatory Files:** `SKILL.md` exists at skill root; `README.md` exists.
- **[5 pts] Valid YAML Frontmatter:** YAML parser validates frontmatter without syntax errors or unescaped characters.
- **[5 pts] Name Conformance:** Name is lowercase kebab-case (1–64 characters), no leading/trailing/consecutive hyphens, and matches parent directory name exactly.
- **[5 pts] Description Quality:** Description is between 1 and 1024 characters, uses third-person active phrasing, and clearly states both *what* the skill does and *when* an agent should trigger it.
- **[5 pts] Relative File Links:** All markdown links to scripts (`scripts/...`) or docs (`references/...`) resolve to real files within the skill root.

---

### Dimension 2: Cross-Platform Portability (20 Points) — `EV-02`
- **[5 pts] No Absolute Paths:** `SKILL.md` and scripts contain zero hardcoded absolute paths (`/Users/...`, `/home/...`, `C:\...`).
- **[5 pts] Cross-Platform Reserved Names:** Neither the skill name nor any file within it uses Windows reserved names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) or tool-reserved names (`synced`).
- **[5 pts] Line Endings & Encodings:** All text files are valid UTF-8 and use standard LF line endings.
- **[5 pts] Portable Interpreter Instructions:** Instructions recommend portable invocation (`python3` / `py`) rather than hardcoded environment paths.

---

### Dimension 3: Documentation & Progressive Disclosure (20 Points) — `EV-03`
- **[5 pts] Concise Main File:** `SKILL.md` is under 500 lines (respecting agent context windows).
- **[5 pts] Progressive Disclosure:** In-depth manuals, schemas, or large references are split into `references/` or `assets/` rather than bloating `SKILL.md`.
- **[5 pts] Examples Included:** At least one concrete usage example with sample user prompt and expected output is provided.
- **[5 pts] Clear Limitations:** Edge cases, failure modes, or prerequisites are explicitly documented.

---

### Dimension 4: Test Coverage & Execution (20 Points) — `EV-04`
- **[5 pts] Test Suite Present:** A `tests/` directory with at least one runnable test file exists.
- **[5 pts] Structural Tests Pass:** Baseline validation and file existence tests execute and pass.
- **[5 pts] Behavioral Execution:** Functional tests execute successfully via `skillfactory test` within the 10-second timeout.
- **[5 pts] Honest Reporting:** Tests do not pass silently with blank assertions; skipped tests are legitimately marked with reasons.

---

### Dimension 5: Code Safety & Secrets Scan (15 Points) — `EV-05`
- **[5 pts] Clean Secret Scan:** Zero hardcoded API keys, bearer tokens, AWS secrets, or private keys detected (`SEC-02`).
- **[5 pts] AST Safety Check:** Python scripts parse cleanly and contain zero high-risk un-sandboxed operations (`eval()`, `exec()`, `shutil.rmtree('/')`, or `shell=True`).
- **[5 pts] Manifest Integrity:** All files match their recorded SHA-256 hashes in `.skillfactory/manifest.json`.

---

## 2. Letter Grades & Quality Gates

| Score | Grade | Meaning & Action |
|---|---|---|
| **90 – 100** | **Grade A** | **Production Ready.** Safe, portable, fully tested, and ready for publication or team sharing. |
| **75 – 89** | **Grade B** | **Good Quality.** Usable and safe, but missing tests, examples, or minor portability improvements. |
| **60 – 74** | **Grade C** | **Scaffold Only.** Functional skeleton, but contains unimplemented test stubs or needs documentation. |
| **0 – 59** | **Grade F** | **Failed Quality Gate.** Critical issues detected (spec violation, unsafe code, or secrets leak). Do not install. |

---

## 3. Host-AI Trigger Rubric (Optional AI Benchmark) — `EV-06`

When running inside an AI host assistant, the assistant can optionally test trigger accuracy by evaluating simulated prompts:

1. **Positive Triggers (Should Activate):**
   - Provide 3 realistic user requests that directly relate to the skill description.
   - Host AI confirms whether the skill's description would clearly trigger activation.
2. **Negative Triggers (Should NOT Activate):**
   - Provide 3 related but distinct requests (e.g., for an Excel comparison skill, test a request about Word documents).
   - Host AI confirms the skill would *not* falsely trigger.
3. **Trigger Specificity:** The skill description avoids generic filler ("Helps the user") that triggers on unrelated tasks.

---

## 4. Evaluation Output Formats

### Plain-Language Summary:
```
Skill Evaluation Report: excel-comparison
Overall Score: 95 / 100 [Grade A]
--------------------------------------------------
[OK] Spec Compliance & Structure:   25 / 25
[OK] Cross-Platform Portability:    20 / 20
[OK] Documentation & Ergonomics:    20 / 20
[OK] Test Coverage & Execution:     15 / 20 (1 test skipped)
[OK] Code Safety & Secrets Scan:    15 / 15
--------------------------------------------------
Recommendation: Ready for installation and publishing.
```

### Structured JSON Output (`--json`):
Saved to `.skillfactory/evaluation.json` with itemized point deductions and remediation suggestions for automated CI gates.
