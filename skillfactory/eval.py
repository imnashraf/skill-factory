"""Skill quality evaluation and scoring engine (Phase 5, Tasks T5.03, T5.05).

Calculates an objective 0–100 quality score across 5 core dimensions:
1. Spec Compliance & Structure (25 pts)
2. Cross-Platform Portability (20 pts)
3. Documentation & Progressive Disclosure (20 pts)
4. Test Coverage & Execution (20 pts)
5. Code Safety & Secrets Scan (15 pts)

Persists results to .skillfactory/evaluation.json (AC5.03, AC5.05).
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from skillfactory.manifest import verify_manifest
from skillfactory.scanner import scan_skill_directory
from skillfactory.spec import WINDOWS_RESERVED_NAMES
from skillfactory.tester import TestRunResult, run_skill_tests
from skillfactory.validator import validate_skill


@dataclass
class DimensionScore:
    name: str
    dimension_id: str
    earned: int
    max_points: int
    items: Dict[str, Tuple[int, int, str]]  # item_name: (earned, max, note)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "dimension_id": self.dimension_id,
            "earned": self.earned,
            "max_points": self.max_points,
            "items": {
                k: {"earned": v[0], "max": v[1], "note": v[2]}
                for k, v in self.items.items()
            },
        }


@dataclass
class EvaluationReport:
    skill_name: str
    skill_dir: str
    total_score: int
    grade: str  # A, B, C, F
    dimensions: List[DimensionScore]
    summary: str
    recommendation: str
    test_result: Optional[Dict[str, Any]] = None
    safety_summary: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "skill_dir": self.skill_dir,
            "total_score": self.total_score,
            "grade": self.grade,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "summary": self.summary,
            "recommendation": self.recommendation,
            "test_result": self.test_result,
            "safety_summary": self.safety_summary,
        }


def calculate_grade(score: int) -> Tuple[str, str]:
    """Return letter grade and recommendation based on 0-100 score."""
    if score >= 90:
        return "Grade A", "Production Ready. Safe, portable, fully tested, and ready for publication."
    elif score >= 75:
        return "Grade B", "Good Quality. Usable and safe, but missing tests, examples, or minor improvements."
    elif score >= 60:
        return "Grade C", "Scaffold Only. Functional skeleton, but contains unimplemented test stubs or needs docs."
    else:
        return "Grade F", "Failed Quality Gate. Critical issues detected (spec violation, unsafe code, or secrets leak)."


def evaluate_skill(
    skill_dir: Path,
    run_tests: bool = True,
    test_timeout: float = 10.0,
    save_report: bool = True,
) -> EvaluationReport:
    """Evaluate an agent skill across all 5 quality dimensions.

    Args:
        skill_dir: Directory containing the skill.
        run_tests: If True, executes skill tests via isolated subprocess.
        test_timeout: Max seconds to wait for tests.
        save_report: If True, writes results to .skillfactory/evaluation.json.

    Returns:
        EvaluationReport containing detailed scores and grade.
    """
    skill_path = Path(skill_dir).resolve()
    skill_name = skill_path.name

    # Pre-flight validation & safety checks
    val_res = validate_skill(skill_path, check_dirname=True, verify_hashes=False)
    safety_rep = scan_skill_directory(skill_path)

    # Dimension 1: Spec Compliance & Structure (25 pts)
    d1_items: Dict[str, Tuple[int, int, str]] = {}
    
    # [5 pts] Mandatory Files: SKILL.md exists, README.md exists
    has_skill_md = (skill_path / "SKILL.md").exists()
    has_readme = (skill_path / "README.md").exists()
    if has_skill_md and has_readme:
        d1_items["mandatory_files"] = (5, 5, "SKILL.md and README.md both exist")
    elif has_skill_md:
        d1_items["mandatory_files"] = (3, 5, "SKILL.md exists, but README.md is missing")
    else:
        d1_items["mandatory_files"] = (0, 5, "Missing required SKILL.md")

    # [5 pts] Valid YAML Frontmatter
    has_yaml_err = any("frontmatter" in e.lower() or "yaml" in e.lower() for e in val_res.errors)
    if not has_yaml_err and has_skill_md:
        d1_items["valid_frontmatter"] = (5, 5, "YAML frontmatter parsed without errors")
    else:
        d1_items["valid_frontmatter"] = (0, 5, "Invalid or unparseable YAML frontmatter")

    # [5 pts] Name Conformance
    has_name_err = any("name" in e.lower() for e in val_res.errors)
    if not has_name_err:
        d1_items["name_conformance"] = (5, 5, "Skill name conforms to lowercase kebab-case rules")
    else:
        d1_items["name_conformance"] = (0, 5, "Skill name violates naming specification")

    # [5 pts] Description Quality
    fm = val_res.metadata.get("frontmatter", {})
    desc = str(fm.get("description", "")).strip() if isinstance(fm, dict) else ""
    if 20 <= len(desc) <= 1024 and ("when" in desc.lower() or "use" in desc.lower() or "provides" in desc.lower() or "helps" in desc.lower()):
        d1_items["description_quality"] = (5, 5, "Description is well-sized and provides trigger guidance")
    elif len(desc) > 0:
        d1_items["description_quality"] = (3, 5, "Description present but could be more specific regarding trigger conditions")
    else:
        d1_items["description_quality"] = (0, 5, "Missing or empty description")

    # [5 pts] Relative File Links
    has_link_err = any("link" in e.lower() or "referenced file" in e.lower() for e in val_res.errors)
    if not has_link_err:
        d1_items["relative_file_links"] = (5, 5, "All markdown file links resolve successfully")
    else:
        d1_items["relative_file_links"] = (0, 5, "Broken markdown file references detected")

    d1_earned = sum(v[0] for v in d1_items.values())
    d1 = DimensionScore("Spec Compliance & Structure", "EV-01", d1_earned, 25, d1_items)

    # Dimension 2: Cross-Platform Portability (20 pts)
    d2_items: Dict[str, Tuple[int, int, str]] = {}

    # [5 pts] No Absolute Paths
    has_abs_err = any("absolute path" in e.lower() for e in val_res.errors)
    if not has_abs_err:
        d2_items["no_absolute_paths"] = (5, 5, "Zero hardcoded absolute paths found")
    else:
        d2_items["no_absolute_paths"] = (0, 5, "Hardcoded absolute paths detected in skill files")

    # [5 pts] Reserved Names
    has_res_err = any(win in skill_name.lower() for win in WINDOWS_RESERVED_NAMES) or skill_name.lower() == "synced"
    for p in skill_path.rglob("*"):
        if p.stem.lower() in WINDOWS_RESERVED_NAMES or p.stem.lower() == "synced":
            has_res_err = True
            break
    if not has_res_err:
        d2_items["reserved_names"] = (5, 5, "Clean of Windows and platform-reserved names")
    else:
        d2_items["reserved_names"] = (0, 5, "Contains Windows or tool reserved device names")

    # [5 pts] Line Endings & Encodings (UTF-8, LF)
    crlf_found = False
    encoding_err = False
    for p in skill_path.rglob("*"):
        if p.is_file() and p.suffix in (".md", ".py", ".json", ".txt", ".sh"):
            try:
                b = p.read_bytes()
                b.decode("utf-8")
                if b"\r\n" in b:
                    crlf_found = True
            except UnicodeDecodeError:
                encoding_err = True
    if not encoding_err and not crlf_found:
        d2_items["line_endings_and_encoding"] = (5, 5, "All text files are valid UTF-8 with standard LF line endings")
    elif not encoding_err:
        d2_items["line_endings_and_encoding"] = (4, 5, "Valid UTF-8, but CRLF line endings detected (consider converting to LF)")
    else:
        d2_items["line_endings_and_encoding"] = (1, 5, "Non-UTF8 file encoding detected")

    # [5 pts] Portable Interpreter Instructions
    skill_md_path = skill_path / "SKILL.md"
    skill_content = skill_md_path.read_text(encoding="utf-8", errors="replace") if skill_md_path.exists() else ""
    hardcoded_interp = bool(re.search(r"/(?:usr|bin|opt)/local/bin/python", skill_content))
    if not hardcoded_interp:
        d2_items["portable_interpreters"] = (5, 5, "Portable invocation patterns used")
    else:
        d2_items["portable_interpreters"] = (2, 5, "Hardcoded system interpreter path found")

    d2_earned = sum(v[0] for v in d2_items.values())
    d2 = DimensionScore("Cross-Platform Portability", "EV-02", d2_earned, 20, d2_items)

    # Dimension 3: Documentation & Progressive Disclosure (20 pts)
    d3_items: Dict[str, Tuple[int, int, str]] = {}

    # [5 pts] Concise Main File (<= 500 lines)
    line_count = len(skill_content.splitlines()) if skill_content else 0
    if line_count <= 500:
        d3_items["concise_main_file"] = (5, 5, f"SKILL.md is concise ({line_count} lines <= 500 limit)")
    else:
        d3_items["concise_main_file"] = (2, 5, f"SKILL.md exceeds recommended 500 lines ({line_count} lines)")

    # [5 pts] Progressive Disclosure (references/ or assets/ or scripts/ used)
    has_refs = (skill_path / "references").is_dir() and any((skill_path / "references").iterdir())
    has_assets = (skill_path / "assets").is_dir() and any((skill_path / "assets").iterdir())
    has_scripts = (skill_path / "scripts").is_dir() and any((skill_path / "scripts").iterdir())
    if has_refs or has_assets or has_scripts:
        d3_items["progressive_disclosure"] = (5, 5, "Progressive disclosure utilized with modular subdirectories")
    else:
        d3_items["progressive_disclosure"] = (3, 5, "Simple flat structure without secondary reference files")

    # [5 pts] Concrete Usage Examples
    has_examples_dir = (skill_path / "examples").is_dir() and any((skill_path / "examples").iterdir())
    has_example_in_md = "## Example" in skill_content or "### Example" in skill_content or "```" in skill_content
    if has_examples_dir or has_example_in_md:
        d3_items["examples_included"] = (5, 5, "Concrete usage examples provided")
    else:
        d3_items["examples_included"] = (1, 5, "No explicit usage examples found")

    # [5 pts] Clear Limitations / Edge Cases
    has_limits = any(
        kw in skill_content.lower()
        for kw in ("limitation", "prerequisite", "edge case", "failure mode", "note:", "important:")
    )
    if has_limits:
        d3_items["limitations_documented"] = (5, 5, "Operational constraints and prerequisites documented")
    else:
        d3_items["limitations_documented"] = (2, 5, "Prerequisites or edge case limitations not explicitly noted")

    d3_earned = sum(v[0] for v in d3_items.values())
    d3 = DimensionScore("Documentation & Progressive Disclosure", "EV-03", d3_earned, 20, d3_items)

    # Dimension 4: Test Coverage & Execution (20 pts)
    d4_items: Dict[str, Tuple[int, int, str]] = {}
    test_run: Optional[TestRunResult] = None

    tests_dir = skill_path / "tests"
    has_tests_dir = tests_dir.is_dir()
    test_files = list(tests_dir.glob("test_*.py")) if has_tests_dir else []

    # [5 pts] Test Suite Present
    if has_tests_dir and len(test_files) > 0:
        d4_items["test_suite_present"] = (5, 5, f"Test suite present with {len(test_files)} test file(s)")
    else:
        d4_items["test_suite_present"] = (0, 5, "No tests/ directory or test files found")

    if run_tests and has_tests_dir and test_files:
        test_run = run_skill_tests(skill_path, timeout=test_timeout, save_report=True)

        # [5 pts] Structural Tests Pass
        if test_run.success and test_run.failures == 0 and test_run.errors == 0:
            d4_items["structural_tests_pass"] = (5, 5, "Baseline test suite executes without failures")
        else:
            d4_items["structural_tests_pass"] = (1, 5, f"Test execution failed with {test_run.failures} failure(s) and {test_run.errors} error(s)")

        # [5 pts] Behavioral Execution (Completed within timeout)
        if not test_run.timed_out:
            d4_items["behavioral_execution"] = (5, 5, f"Tests ran successfully in {test_run.duration_sec:.2f}s (< {test_timeout}s timeout)")
        else:
            d4_items["behavioral_execution"] = (0, 5, f"Tests timed out after {test_timeout}s")

        # [5 pts] Honest Reporting
        if test_run.tests_run > 0 and test_run.failures == 0:
            if test_run.skipped > 0:
                d4_items["honest_reporting"] = (4, 5, f"{test_run.tests_run} tests run, {test_run.skipped} legitimately marked skipped")
            else:
                d4_items["honest_reporting"] = (5, 5, f"All {test_run.tests_run} assertions executed and verified")
        elif test_run.tests_run > 0:
            d4_items["honest_reporting"] = (1, 5, "Test suite reported failing assertions")
        else:
            d4_items["honest_reporting"] = (0, 5, "0 test assertions were executed")
    else:
        # If no tests or tests skipped
        if not has_tests_dir or not test_files:
            d4_items["structural_tests_pass"] = (0, 5, "No tests to execute")
            d4_items["behavioral_execution"] = (0, 5, "Execution skipped (no tests)")
            d4_items["honest_reporting"] = (0, 5, "No assertions verified")
        else:
            d4_items["structural_tests_pass"] = (3, 5, "Test files present (execution skipped)")
            d4_items["behavioral_execution"] = (3, 5, "Execution skipped per user flag")
            d4_items["honest_reporting"] = (3, 5, "Execution skipped per user flag")

    d4_earned = sum(v[0] for v in d4_items.values())
    d4 = DimensionScore("Test Coverage & Execution", "EV-04", d4_earned, 20, d4_items)

    # Dimension 5: Code Safety & Secrets Scan (15 pts)
    d5_items: Dict[str, Tuple[int, int, str]] = {}

    # [5 pts] Clean Secret Scan
    secret_findings = [f for f in safety_rep.findings if f.rule_id.startswith("SEC")]
    if len(secret_findings) == 0:
        d5_items["clean_secret_scan"] = (5, 5, "Zero credentials, API tokens, or private keys detected")
    else:
        d5_items["clean_secret_scan"] = (0, 5, f"Detected {len(secret_findings)} hardcoded secret pattern(s)")

    # [5 pts] AST Safety Check
    ast_findings = [f for f in safety_rep.findings if f.severity in ("CRITICAL", "HIGH") and f.rule_id.startswith("AST")]
    if len(ast_findings) == 0:
        d5_items["ast_safety_check"] = (5, 5, "AST scan clean: 0 dangerous dynamic execution or shell=True calls")
    else:
        d5_items["ast_safety_check"] = (0, 5, f"Detected {len(ast_findings)} dangerous AST construct(s)")

    # [5 pts] Manifest Integrity
    manifest_path = skill_path / ".skillfactory" / "manifest.json"
    if manifest_path.exists():
        valid_hashes, discrepancies = verify_manifest(skill_path)
        if valid_hashes:
            d5_items["manifest_integrity"] = (5, 5, "All files match their recorded SHA-256 manifest hashes")
        else:
            d5_items["manifest_integrity"] = (1, 5, f"Manifest hash mismatch detected: {len(discrepancies)} file(s) altered")
    else:
        d5_items["manifest_integrity"] = (3, 5, "Manifest file not found (unmanaged or freshly generated without manifest)")

    d5_earned = sum(v[0] for v in d5_items.values())
    d5 = DimensionScore("Code Safety & Secrets Scan", "EV-05", d5_earned, 15, d5_items)

    # Total Calculation
    total_score = d1_earned + d2_earned + d3_earned + d4_earned + d5_earned
    total_score = max(0, min(100, total_score))
    grade, recommendation = calculate_grade(total_score)

    report = EvaluationReport(
        skill_name=skill_name,
        skill_dir=str(skill_path),
        total_score=total_score,
        grade=grade,
        dimensions=[d1, d2, d3, d4, d5],
        summary=f"Skill Quality Score: {total_score} / 100 [{grade}]",
        recommendation=recommendation,
        test_result=test_run.to_dict() if test_run else None,
        safety_summary=safety_rep.to_dict(),
    )

    if save_report:
        _save_evaluation_report(skill_path, report)

    return report


def _save_evaluation_report(skill_path: Path, report: EvaluationReport) -> None:
    """Save evaluation report to .skillfactory/evaluation.json (AC5.05)."""
    meta_dir = skill_path / ".skillfactory"
    meta_dir.mkdir(parents=True, exist_ok=True)
    eval_file = meta_dir / "evaluation.json"

    data = report.to_dict()
    data["timestamp"] = datetime.now(timezone.utc).isoformat()

    try:
        eval_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except Exception:
        pass
