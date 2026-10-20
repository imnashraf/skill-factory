# Phase 17 Implementation Plan: Skill Library, Discovery & Community Ecosystem

This document establishes the technical blueprint, architectural components, implementation tasks, and validation strategy for Phase 17.

---

## 1. Objectives & Scope

Phase 17 builds a robust, offline-capable, and community-ready discovery and sharing ecosystem for Skill Factory without relying on paid backends or mandatory cloud services.

### Workstream Overview

1. **Workstream 17A — Extensible 3-Tier Domain Taxonomy (`FR17-01`)**:
   - Establish formal 3-tier classification:
     - **Personal**: Productivity, Learning, File management, Research, Travel, Personal administration.
     - **Professional**: Finance, Accounting, Human resources, Payroll, Procurement, Supply chain, Project management, ERP, Real estate, Education, Legal operations, Healthcare administration, Public administration.
     - **Developer and AI**: Software engineering, Cybersecurity, DevOps, Testing, Data engineering, AI engineering, Agent orchestration, Documentation, Release management.
   - Dynamic domain/category registration in `skillfactory/library.py`.
2. **Workstream 17B — Multi-Attribute Offline Catalog Search (`FR17-02`)**:
   - Enhance `skillfactory search` and `search_catalog()` with multi-attribute filtering:
     - `--domain`, `--category`, `--platform`, `--grade`, `--type`.
   - Maintain sub-10ms offline search budget.
3. **Workstream 17C — Curated Skill Packs Lifecycle & Preview (`FR17-03`)**:
   - Implement `preview_pack()` in `skillfactory/pack.py` with pre-installation conflict detection, dependency resolution, and file lists.
   - Add CLI command `skillfactory pack preview <pack>`.
   - Verify all 5 curated packs (14 reference skills) have deterministic tests, working logic, and atomic rollback.
4. **Workstream 17D — Community Contribution Automated Screening (`FR17-04`, `FR17-05`)**:
   - Implement `scripts/validate_submission.py` for automated PR screening.
   - Strict security quarantine: Untrusted submitted code is screened via AST and static linters; never executed automatically in CI without explicit sandboxed user approval.
   - Quality scoring and review checklist generation.
5. **Workstream 17E — Offline Markdown Catalog (`FR17-06`)**:
   - Generate standalone offline documentation `docs/SKILL_CATALOG.md` detailing all domains, packs, platforms, and skills.

---

## 2. Technical Architecture

### 2.1 Domain Taxonomy Registry (`skillfactory/library.py`)

```text
Taxonomy Hierarchy:
├── Personal (6 categories)
├── Professional (13 categories)
└── Developer and AI (9 categories)
      └── Dynamic Registration API: register_custom_domain(domain, categories)
```

### 2.2 Pack Preview & Conflict Detection (`skillfactory/pack.py`)

```text
skillfactory pack preview <pack_id>
  │
  ├── 1. Resolves skill dependencies and directory paths
  ├── 2. Checks target platform directory for existing skills (Conflict Detection)
  ├── 3. Verifies manifests and SHA-256 integrity
  └── 4. Outputs structured file tree, platform compatibility, and conflict status
```

### 2.3 Community Submission Quarantine (`scripts/validate_submission.py`)

```text
Incoming PR / Contributed Skill Directory
  │
  ├── [Step 1: Manifest & Hash Check] (SHA-256 integrity)
  ├── [Step 2: YAML Frontmatter & Spec Check] (Schema validation)
  ├── [Step 3: AST Safety Screening] (Rejects eval, exec, shell=True, network calls)
  ├── [Step 4: Quality Scoring] (Static evaluation)
  └── [Quarantine Barrier]: Subprocess execution is BLOCKED by default unless
      explicitly authorized with --run-untrusted in an isolated container.
```

---

## 3. Implementation Steps

1. **Step 17.1**: Update `skillfactory/library.py` to incorporate the 3-tier taxonomy, dynamic registration, and multi-attribute search filters (`domain`, `category`, `platform`, `grade`, `template_family`).
2. **Step 17.2**: Update `skillfactory/pack.py` with `preview_pack()` and conflict detection.
3. **Step 17.3**: Update `skillfactory/cli.py` to wire `skillfactory search` options (`--domain`, `--category`, `--platform`, `--grade`, `--type`) and `skillfactory pack preview`.
4. **Step 17.4**: Implement `scripts/validate_submission.py` with strict security quarantine.
5. **Step 17.5**: Generate `docs/SKILL_CATALOG.md` covering all 14 reference skills, 5 curated packs, and 31 domains.
6. **Step 17.6**: Add unit and integration tests in `tests/test_library_search.py` and `tests/test_pack_preview.py`.
7. **Step 17.7**: Verify all tests pass, benchmark search performance, and generate `docs/final-development/phase17Report.md`.
