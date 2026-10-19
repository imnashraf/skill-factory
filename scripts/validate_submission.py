#!/usr/bin/env python3
"""Community Skill Submission Screening & Quarantine Validator (Phase 17, Workstream 17D).

Automates PR validation for community skill submissions with strict security quarantine:
1. Manifest integrity & SHA-256 digest validation.
2. YAML frontmatter, naming, and specification conformity checks.
3. Strict AST security analysis and credentials scan.
4. Quarantine barrier: Untrusted community code is NEVER executed automatically.
5. Automated PR Review Checklist generation in Markdown.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from skillfactory.eval import evaluate_skill
from skillfactory.manifest import verify_manifest
from skillfactory.scanner import scan_skill_directory
from skillfactory.validator import validate_skill


def validate_submission(skill_dir: Path, allow_untrusted_exec: bool = False) -> tuple[int, str]:
    """Screen an incoming skill submission under security quarantine."""
    path = Path(skill_dir).resolve()
    if not path.is_dir() or not (path / "SKILL.md").is_file():
        return 1, f"Error: '{path}' is not a valid Agent Skill directory (missing SKILL.md)."

    skill_name = path.name
    checklist_lines: list[str] = [
        f"## Automated Community Submission Screening: `{skill_name}`",
        "",
        "### 1. Security & Quarantine Screening",
    ]

    # Step 1: Manifest Integrity Check
    manifest_file = path / ".skillfactory" / "manifest.json"
    if manifest_file.is_file():
        m_valid, m_errors = verify_manifest(path)
        if m_valid:
            checklist_lines.append("- [x] **Manifest Integrity**: SHA-256 digests match recorded files.")
        else:
            checklist_lines.append(f"- [ ] **Manifest Integrity**: FAIL ({'; '.join(m_errors)})")
    else:
        m_valid = False
        checklist_lines.append("- [ ] **Manifest Integrity**: FAIL (Missing `.skillfactory/manifest.json`)")

    # Step 2: Specification & Structure Validation
    val_report = validate_skill(path)
    if val_report.is_valid:
        checklist_lines.append("- [x] **Spec Compliance**: Valid YAML frontmatter, kebab-case naming, and file hierarchy.")
    else:
        checklist_lines.append(f"- [ ] **Spec Compliance**: FAIL ({'; '.join(val_report.errors)})")

    # Step 3: AST Security & Secrets Quarantine Scan
    sec_report = scan_skill_directory(path)
    if sec_report.is_clean:
        checklist_lines.append(f"- [x] **AST Safety Scan**: Clean ({sec_report.files_scanned} files scanned, 0 high/critical findings).")
    else:
        criticals = [f"{f.rule_id} in {f.file_path}: {f.description}" for f in sec_report.findings if f.severity in ("CRITICAL", "HIGH")]
        checklist_lines.append(f"- [ ] **AST Safety Scan**: FAIL ({len(criticals)} critical violations: {'; '.join(criticals)})")

    # Step 4: Quarantine Rule Enforcement
    checklist_lines.extend([
        "",
        "### 2. Execution Quarantine Policy",
    ])
    if not allow_untrusted_exec:
        checklist_lines.append("- [x] **Quarantine Barrier Enforced**: Untrusted code was NOT executed automatically.")
        checklist_lines.append("  *(To authorize test execution in an isolated sandbox, pass `--run-untrusted`)*")
    else:
        checklist_lines.append("- [!] **Quarantine Override**: Subprocess test execution was explicitly authorized by operator.")

    # Step 5: Static Quality Evaluation
    eval_rep = evaluate_skill(path, run_tests=allow_untrusted_exec, save_report=False)
    checklist_lines.extend([
        "",
        "### 3. Static Quality Evaluation",
        f"- **Quality Score**: {eval_rep.total_score}/100 [{eval_rep.grade}]",
        f"- **Recommendation**: {eval_rep.recommendation}",
        "",
        "### 4. Maintainer Review Action Required",
    ])

    overall_pass = m_valid and val_report.is_valid and sec_report.is_clean

    if overall_pass:
        checklist_lines.extend([
            "- [x] Automated static screening passed.",
            "- [ ] Maintainer manual code review pending.",
            "- [ ] Approved for integration into domain library.",
            "",
            "> **VERDICT: AUTOMATED STATIC SCREENING PASSED. READY FOR MAINTAINER REVIEW.**",
        ])
        exit_code = 0
    else:
        checklist_lines.extend([
            "- [ ] Automated screening rejected due to above violations.",
            "- [ ] Contributor remediation required before merge.",
            "",
            "> **VERDICT: AUTOMATED SCREENING FAILED. CORRECT FINDINGS BEFORE RESUBMITTING.**",
        ])
        exit_code = 1

    return exit_code, "\n".join(checklist_lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Screen community skill submissions under strict security quarantine.")
    parser.add_argument("skill_dir", help="Path to contributed skill folder")
    parser.add_argument("--run-untrusted", action="store_true", help="Explicit operator override to run tests on untrusted code in local environment")
    parser.add_argument("--json", action="store_true", help="Output screening report in JSON format")
    args = parser.parse_args()

    skill_path = Path(args.skill_dir)
    code, report_md = validate_submission(skill_path, allow_untrusted_exec=args.run_untrusted)

    if args.json:
        output = {
            "status": "passed" if code == 0 else "failed",
            "skill_name": skill_path.name,
            "exit_code": code,
            "markdown_report": report_md,
        }
        print(json.dumps(output, indent=2))
    else:
        print(report_md)

    return code


if __name__ == "__main__":
    sys.exit(main())
