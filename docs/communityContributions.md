# Community Skill Contribution Guidelines

Skill Factory welcomes community contributions of reusable, validated Agent Skills. This guide outlines the submission workflow, quality standards, security requirements, and maintainer review process to ensure the ecosystem remains safe, reliable, and completely local-first.

---

## 1. Core Principles

All community-submitted skills must uphold Skill Factory's foundational principles:

- **Local-First & Offline:** Pure Python standard library implementation (3.9+). No mandatory cloud backends, accounts, API keys, or tracking telemetry.
- **Auditable & Deterministic:** Clean, readable Python scripts with deterministic behavior, clear error reporting, and automated unit tests.
- **Security by Default:** Untrusted by default. Zero hardcoded secrets, zero arbitrary dynamic code execution (`eval`, `exec`), and zero remote execution pipelines (`curl | bash`).
- **Honest Documentation:** Clear operational boundaries. Never claim autonomous activation or cross-platform compatibility without test verification.

---

## 2. Submission Workflow

```text
Fork Repository ──> Scaffold Skill ──> Implement Logic ──> Add Tests ──> Validate & Scan ──> Submit PR
```

### Step 1: Scaffold Your Skill

Scaffold a compliant Agent Skill package using Skill Factory:

```bash
skillfactory new my-community-skill --template python-script --output generated-skills
```

### Step 2: Implement Functional Logic

Implement deterministic task logic in `scripts/main.py`:

- Use standard library modules (`csv`, `json`, `pathlib`, `re`, `urllib.parse`, etc.).
- Avoid third-party dependencies unless strictly justified and verified in an isolated environment.
- Implement actionable CLI arguments with `--json` support for programmatic integration.

### Step 3: Implement Automated Tests

Provide meaningful tests in `tests/`:

- Test happy paths with realistic input fixtures.
- Test error conditions (missing files, malformed inputs, permission errors).
- Tests must execute in under 10 seconds without external network access.

### Step 4: Run Validation and Quality Audits

Run the full local validation suite:

```bash
# 1. Structural and frontmatter validation
skillfactory validate generated-skills/my-community-skill

# 2. Automated test execution in subprocess isolation
skillfactory test generated-skills/my-community-skill

# 3. Static AST safety and secret scan
skillfactory scan generated-skills/my-community-skill

# 4. Multi-dimensional quality evaluation
skillfactory eval generated-skills/my-community-skill
```

To be eligible for maintainer review, your skill must achieve a **minimum score of 80 / 100 [Grade B]**. Grade A (>= 90/100) is strongly recommended for inclusion in the reference catalog.

### Step 5: Submit Pull Request

1. Commit your skill to a feature branch: `git checkout -b skill/my-community-skill`.
2. Ensure directory matches the standard structure:

   ```text
   generated-skills/my-community-skill/
   ├── .skillfactory/
   │   ├── manifest.json
   │   └── skill-spec.json
   ├── LICENSE
   ├── README.md
   ├── SKILL.md
   ├── examples/
   │   └── example.md
   ├── references/
   │   └── guide.md
   ├── scripts/
   │   └── main.py
   └── tests/
       └── test_main.py
   ```

3. Open a Pull Request referencing the Skill Submission template.

---

## 3. Required Metadata

The frontmatter of `SKILL.md` must contain:

```yaml
---
name: my-community-skill
description: Clear, action-oriented description explaining what the skill does and when an agent should trigger it.
version: 1.0.0
author: Contributor Name <contributor@example.com>
license: MIT
compatibility: Claude Code, Google Antigravity, Cursor, OpenAI Codex
metadata:
  tags:
    - automation
    - data
    - utility
---
```

- **Name:** Lowercase alphanumeric and hyphens (1–64 characters).
- **Description:** 10–1024 characters. Must include triggering guidance.
- **License:** Permissive open-source license (MIT, Apache-2.0, Unlicense).

---

## 4. Rejection Criteria

Submissions will be rejected if they contain:

1. **Security Violations:** Hardcoded API keys, private keys, dangerous dynamic calls (`eval`, `exec`), or prompt injection attempts.
2. **Untrusted Remote Dependencies:** Shell pipelines (`curl ... | bash`), mandatory paid APIs, or external SaaS subscriptions.
3. **Missing or Non-Functional Tests:** Empty test directories or placeholder tests (`test_placeholder.py`) with zero functional assertions.
4. **Misleading Documentation:** Claiming autonomous agent activation or cross-platform features without verified test evidence.
5. **Path Traversal & Destructive Operations:** Directory deletion outside the designated workspace boundary or Zip-Slip vulnerabilities.

---

## 5. Maintainer Review Process

Every community submission undergoes:

1. **Automated CI Validation:** Spec conformance, test execution (< 10s timeout), AST safety scan, and quality scoring.
2. **Manual Code Audit:** Review of `scripts/main.py` for edge-case handling, resource safety, and input sanitization.
3. **Multi-Agent Compatibility Check:** Verification that `SKILL.md` triggers appropriately across supported AI assistants.
4. **Catalog Inclusion:** Upon approval, the skill is indexed into `skillfactory/data/catalog.json`.
