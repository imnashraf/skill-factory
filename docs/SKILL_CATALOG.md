# Skill Factory: Offline Skill Catalog & Domain Taxonomy

Welcome to the **Skill Factory Offline Skill Catalog**. This document catalogs all reference skills, curated domain packs, and the 3-tier taxonomy. All skills listed below operate with **100% Python Standard Library compliance** (zero third-party dependencies) and adhere to strict security quarantine controls.

---

## 1. The 3-Tier Domain Taxonomy

Skill Factory organizes skills into three main domains and 31 domain categories. This taxonomy is extensible via `skillfactory.library.register_custom_domain()`.

```text
├── 1. Personal
│   ├── Productivity
│   ├── Learning
│   ├── File management
│   ├── Research
│   ├── Travel
│   └── Personal administration
│
├── 2. Professional
│   ├── Finance
│   ├── Accounting
│   ├── Human resources
│   ├── Payroll
│   ├── Procurement
│   ├── Supply chain
│   ├── Project management
│   ├── ERP
│   ├── Real estate
│   ├── Education
│   ├── Legal operations
│   ├── Healthcare administration
│   └── Public administration
│
└── 3. Developer and AI
    ├── Software engineering
    ├── Cybersecurity
    ├── DevOps
    ├── Testing
    ├── Data engineering
    ├── AI engineering
    ├── Agent orchestration
    ├── Documentation
    └── Release management
```

---

## 2. Curated Domain Skill Packs

Skill Factory ships with 5 pre-packaged domain packs that can be previewed, batch-installed, verified, and uninstalled across any supported AI coding assistant.

| Pack ID | Pack Name | Domain Category | Skills Included | Avg Score |
| :--- | :--- | :--- | :--- | :--- |
| `office-productivity` | Office Productivity Pack | Personal: Productivity | `csv-to-report`, `excel-comparison`, `file-organizer`, `markdown-doc-validator`, `structured-notes-formatter` | **98 / 100** |
| `finance-erp` | Finance & ERP Suite | Professional: Finance | `financial-variance-analyzer`, `invoice-reconciliation`, `timesheet-reconciliation` | **95 / 100** |
| `hr-workforce` | HR & Workforce Operations | Professional: Human Resources | `attendance-csv-validator`, `timesheet-reconciliation`, `structured-notes-formatter` | **95 / 100** |
| `project-management` | Agile Project Operations | Professional: Project Mgmt | `project-status-reporter`, `raid-log-validator`, `markdown-doc-validator` | **97 / 100** |
| `developer-security` | Developer & Security Suite | Developer: DevOps & Security | `dependency-manifest-reviewer`, `security-config-scanner`, `test-inventory-analyzer` | **96 / 100** |

---

## 3. Reference Skills Directory (14 Production-Grade Skills)

Every skill listed below has been independently tested, AST scanned, evaluated, and verified.

### 3.1 Personal Domain Skills

#### `excel-comparison`

- **Domain / Category**: Personal / Productivity
- **Description**: Compares two Excel / tabular data files row-by-row and generates difference reports.
- **Quality Score**: 98 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <file1> <file2>`

#### `csv-to-report`

- **Domain / Category**: Personal / Productivity
- **Description**: Parses CSV files, validates numeric columns, and produces formatted Markdown summary reports.
- **Quality Score**: 99 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <input.csv>`

#### `file-organizer`

- **Domain / Category**: Personal / File Management
- **Description**: Inspects target folders, categorizes files by extension and MIME group, and generates reorganization plans.
- **Quality Score**: 97 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <target_dir>`

#### `markdown-doc-validator`

- **Domain / Category**: Personal / Documentation
- **Description**: Validates Markdown document integrity, broken relative links, heading hierarchy, and frontmatter.
- **Quality Score**: 98 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <docs_dir>`

#### `structured-notes-formatter`

- **Domain / Category**: Personal / Learning & Productivity
- **Description**: Normalizes raw text notes into structured Markdown with action items and key takeaways.
- **Quality Score**: 98 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <notes.txt>`

---

### 3.2 Professional Domain Skills

#### `attendance-csv-validator`

- **Domain / Category**: Professional / Human Resources
- **Description**: Validates employee attendance logs, timestamps, employee IDs, and flags anomalies.
- **Quality Score**: 93 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <attendance.csv>`

#### `financial-variance-analyzer`

- **Domain / Category**: Professional / Finance
- **Description**: Calculates financial budget vs. actual variances, percentage changes, and highlights over-budget items.
- **Quality Score**: 95 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <financial.csv>`

#### `invoice-reconciliation`

- **Domain / Category**: Professional / Finance & Accounting
- **Description**: Reconciles billing records, matches purchase orders, and flags duplicate or mismatched invoices.
- **Quality Score**: 95 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <invoices.csv>`

#### `project-status-reporter`

- **Domain / Category**: Professional / Project Management
- **Description**: Aggregates sprint tasks, calculates completion velocity, and generates stakeholder status briefs.
- **Quality Score**: 97 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <tasks.csv>`

#### `raid-log-validator`

- **Domain / Category**: Professional / Project Management
- **Description**: Reviews project RAID (Risks, Assumptions, Issues, Dependencies) logs and flags unassigned critical risks.
- **Quality Score**: 96 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <raid_log.csv>`

#### `timesheet-reconciliation`

- **Domain / Category**: Professional / Payroll & Workforce
- **Description**: Cross-references employee timesheets with billing project codes and flags hour discrepancies.
- **Quality Score**: 96 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <timesheet.csv>`

---

### 3.3 Developer and AI Domain Skills

#### `dependency-manifest-reviewer`

- **Domain / Category**: Developer / Software Engineering & Security
- **Description**: Parses `pyproject.toml`, `requirements.txt`, and `package.json` to flag pinned version risks and license conflicts.
- **Quality Score**: 96 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <manifest_file>`

#### `security-config-scanner`

- **Domain / Category**: Developer / Cybersecurity & DevOps
- **Description**: Audits configuration files (JSON, YAML, INI) for hardcoded secrets, permissive permissions, and insecure defaults.
- **Quality Score**: 96 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <config_dir>`

#### `test-inventory-analyzer`

- **Domain / Category**: Developer / Testing & QA
- **Description**: Inspects `tests/` directories, catalogs test cases, identifies missing assertions, and calculates test density.
- **Quality Score**: 96 / 100 (Grade A)
- **Security Status**: Clean (0 findings)
- **Command**: `python scripts/main.py <tests_dir>`

---

## 4. Offline Discovery & Pack Lifecycle Workflows

### Multi-Attribute Offline Search

Filter the offline catalog across multiple criteria in under 10ms:

```bash
# Keyword search
skillfactory search "invoice"

# Search by domain
skillfactory search --domain "Professional"

# Multi-attribute search
skillfactory search --category "Finance" --grade "A" --type "python-script"
```

### Pack Lifecycle Operations

```bash
# 1. Preview file operations and detect conflicts before installing
skillfactory pack preview office-productivity --target claude-code

# 2. Install all skills in a pack with atomic rollback on error
skillfactory pack install office-productivity --target claude-code

# 3. Verify all installed pack skills
skillfactory pack verify office-productivity

# 4. Clean uninstallation
skillfactory pack uninstall office-productivity --target claude-code
```
