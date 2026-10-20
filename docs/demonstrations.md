# Skill Factory — Reproducible Reference Demonstrations

This document provides reproducible, end-to-end demonstrations for Skill Factory's five generated reference skills. Each demonstration uses self-contained input fixtures, standard command invocations, and verifiable outputs.

All demonstrations run locally on pure Python standard library (3.9+) with **zero external dependencies**.

---

## Automated Execution Suite

You can execute all five demonstrations automatically in one step:

```bash
python3 scripts/run_demos.py
```

Expected output ends with:

```text
======================================================================
 DEMONSTRATION SUITE SUMMARY
======================================================================
  [PASS] excel-comparison
  [PASS] security-config-scanner
  [PASS] file-organizer
  [PASS] csv-to-report
  [PASS] markdown-doc-validator

All 5 demonstrations executed successfully with verifiable outputs!
```

---

## 1. Excel & CSV Comparison Engine (`excel-comparison`)

### Objective

Detect structural modifications, cell-level changes, inserted records, and deleted records between two CSV/XLSX files using a unique primary key column or ordinal row index.

### Input Fixtures

`q1_budget.csv`:

```csv
id,department,allocated,spent
101,Engineering,150000,142000
102,Marketing,80000,79500
103,Design,45000,41000
```

`q2_budget.csv`:

```csv
id,department,allocated,spent
101,Engineering,160000,158000
102,Marketing,80000,79500
104,Security,60000,32000
```

### Execution Command

```bash
python3 generated-skills/excel-comparison/scripts/main.py \
  q1_budget.csv q2_budget.csv \
  --key id \
  --json
```

### Output Summary

```json
{
  "is_identical": false,
  "total_rows_file1": 3,
  "total_rows_file2": 3,
  "added_count": 1,
  "removed_count": 1,
  "modified_count": 1,
  "identical_count": 1,
  "diffs": [
    {
      "key_value": "103",
      "diff_type": "removed"
    },
    {
      "key_value": "104",
      "diff_type": "added"
    },
    {
      "key_value": "101",
      "diff_type": "modified",
      "cell_diffs": [
        {"column": "allocated", "old_value": "150000", "new_value": "160000"},
        {"column": "spent", "old_value": "142000", "new_value": "158000"}
      ]
    }
  ]
}
```

---

## 2. Security & Configuration Scanner (`security-config-scanner`)

### Objective

Scan directories recursively for exposed API keys, private keys, database credentials, and insecure configuration attributes (such as enabled debug mode and wildcard CORS headers).

### Input Fixture

`app_config.py`:

```python
DEBUG = True
origin = "*"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
```

### Execution Command

```bash
python3 generated-skills/security-config-scanner/scripts/main.py \
  ./demo_dir \
  --json
```

### Output Summary

```json
{
  "status": "success",
  "total_findings": 2,
  "findings": [
    {
      "rule_id": "CFG-02",
      "rule_title": "Debug Mode Enabled",
      "severity": "MEDIUM",
      "file_path": "app_config.py",
      "line_number": 1,
      "remediation": "Ensure debug mode is disabled in production configurations."
    },
    {
      "rule_id": "SEC-01",
      "rule_title": "AWS Access Key ID",
      "severity": "CRITICAL",
      "file_path": "app_config.py",
      "line_number": 3,
      "remediation": "Revoke key immediately and rotate IAM credentials."
    }
  ]
}
```

---

## 3. Smart File Organizer & Renamer (`file-organizer`)

### Objective

Categorize mixed-format files into structured subdirectories (`documents/`, `images/`, `scripts/`, `archives/`), sanitize spaces and special characters with underscores, and handle filename collisions deterministically.

### Input Fixture

A folder with unorganized files:

```text
inbox/
├── annual report 2026.pdf
├── screenshot 2026-10-19.png
├── backup script.py
└── archive.tar.gz
```

### Execution Command

```bash
python3 generated-skills/file-organizer/scripts/main.py \
  inbox \
  --sanitize \
  --json
```

### Output Summary

```json
{
  "status": "success",
  "files_organized": 4,
  "operations": [
    {
      "source_path": "inbox/annual report 2026.pdf",
      "target_path": "inbox/documents/annual_report_2026.pdf",
      "category": "documents",
      "renamed": true
    },
    {
      "source_path": "inbox/screenshot 2026-10-19.png",
      "target_path": "inbox/images/screenshot_2026-10-19.png",
      "category": "images",
      "renamed": true
    },
    {
      "source_path": "inbox/backup script.py",
      "target_path": "inbox/scripts/backup_script.py",
      "category": "scripts",
      "renamed": true
    },
    {
      "source_path": "inbox/archive.tar.gz",
      "target_path": "inbox/archives/archive.tar.gz",
      "category": "archives",
      "renamed": false
    }
  ]
}
```

---

## 4. CSV Analytical Report Generator (`csv-to-report`)

### Objective

Generate statistical distribution profiles and GitHub-flavored markdown or HTML summary reports from tabular CSV files.

### Input Fixture

`server_metrics.csv`:

```csv
timestamp,cpu_usage,memory_mb,active_sessions
2026-10-19T10:00:00,12.5,410,120
2026-10-19T10:05:00,45.2,650,280
2026-10-19T10:10:00,78.9,820,410
2026-10-19T10:15:00,23.1,490,190
```

### Execution Command

```bash
python3 generated-skills/csv-to-report/scripts/main.py \
  server_metrics.csv \
  --format markdown \
  --title "Server Health Summary"
```

### Output Summary

```markdown
# Server Health Summary

- **Total Rows:** 4
- **Total Columns:** 4

## Numeric Column Metrics

| Column | Type | Nulls | Min | Max | Mean | Sum |
| --- | --- | --- | --- | --- | --- | --- |
| **cpu_usage** | `float` | 0 | 12.5 | 78.9 | 39.93 | 159.7 |
| **memory_mb** | `int` | 0 | 410.0 | 820.0 | 592.5 | 2370.0 |
| **active_sessions** | `int` | 0 | 120.0 | 410.0 | 250.0 | 1000.0 |
```

---

## 5. Markdown Documentation Validator (`markdown-doc-validator`)

### Objective

Audit markdown files across a documentation tree for broken relative links, missing code block language specifiers, heading level jumps, and missing document titles.

### Input Fixtures

`sample_doc.md`:

````markdown
# Sample Documentation

Valid link: [Guide](guide.md)
Broken link: [Missing](does_not_exist.md)

```
echo 'unannotated fence'
```
````

`guide.md`:

```markdown
# Guide

All good.
```

### Execution Command

```bash
python3 generated-skills/markdown-doc-validator/scripts/main.py \
  ./demo_dir \
  --json
```

### Output Summary

```json
{
  "status": "success",
  "total_issues": 2,
  "errors": 1,
  "warnings": 1,
  "issues": [
    {
      "file_path": "sample_doc.md",
      "line_number": 4,
      "rule_id": "MD-BROKEN-LINK",
      "severity": "ERROR",
      "message": "Broken relative link: 'does_not_exist.md' points to nonexistent path"
    },
    {
      "file_path": "sample_doc.md",
      "line_number": 6,
      "rule_id": "MD-FENCE-LANG",
      "severity": "WARNING",
      "message": "Code block missing language tag"
    }
  ]
}
```

---

## Video / Screencast Recording Script

For maintainers or community members recording terminal demonstrations:

1. **Window Size:** Set terminal to 80x24 or 120x30 characters.
2. **Font:** Use a legible monospace font at 16pt (e.g., JetBrains Mono, Fira Code).
3. **Execution Sequence:**
   - Run `skillfactory --help` to show core commands.
   - Run `python3 scripts/run_demos.py` to demonstrate all five reference skills in action.
   - Run `skillfactory new my-demo-skill` to demonstrate the scaffold command.
   - Run `skillfactory install generated-skills/csv-to-report --platform claude` to demonstrate platform installation.
4. **Authenticity Notice:** Never mock or fabricate terminal execution. Run the commands directly in an active shell session.
