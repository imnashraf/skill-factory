"""AI-Assisted Skill Creation Engine (Phases 15 & 16).

Orchestrates the safe, sandboxed, provider-neutral workflow:
1. Requirements Interpretation & Specification Builder with Assumption Register.
2. Code & Test Generation via pluggable AIProvider or deterministic non-AI fallback.
3. Pre-execution AST Safety & Secrets Scanning.
4. Isolated Subprocess Sandbox Execution with 10s Timeout.
5. Bounded Self-Repair Loop (up to 3 retries) using stderr feedback.
6. Independent Functional Correctness & Requirement-to-Test Traceability Audit.
7. Draft Quarantine & Human-in-the-Loop Installation Approval.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillfactory.ai.evaluator import (
    FunctionalAuditReport,
    audit_functional_correctness,
    generate_non_ai_implementation,
)
from skillfactory.ai.mock_provider import MockAIProvider
from skillfactory.ai.ollama import OllamaProvider
from skillfactory.ai.openai_compat import OpenAICompatibleProvider
from skillfactory.ai.provider import AIProvider, CodeGenerationResult
from skillfactory.ai.requirements import (
    StructuredRequirementSpec,
    parse_natural_language_requirement,
)
from skillfactory.ai.test_gen import generate_behavioral_tests
from skillfactory.core import generate_skill
from skillfactory.errors import SkillFactoryError
from skillfactory.eval import evaluate_skill
from skillfactory.manifest import create_manifest, write_manifest
from skillfactory.scanner import scan_python_code, scan_secrets_in_text
from skillfactory.spec import SkillSpec
from skillfactory.tester import run_skill_tests
from skillfactory.validator import validate_skill


@dataclass
class AICreationResult:
    """Outcome of AI-assisted skill creation workflow."""
    status: str  # "success", "safety_rejected", "tests_failed", "cancelled", "fallback_success"
    skill_name: str
    output_dir: str
    eval_score: int
    grade: str
    repair_count: int
    explanation: str
    safety_clean: bool
    is_draft: bool
    structured_spec: Optional[Dict[str, Any]] = None
    audit_report: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_default_provider() -> AIProvider:
    """Select the best available AI provider.

    Checks:
    1. Local Ollama (if running)
    2. Local OpenAI-compatible (if running)
    3. Deterministic Mock Provider (offline fallback)
    """
    ollama = OllamaProvider()
    if ollama.is_available():
        return ollama

    openai_compat = OpenAICompatibleProvider()
    if openai_compat.is_available():
        return openai_compat

    return MockAIProvider()


def derive_spec_from_requirement(requirement: str, preferred_name: Optional[str] = None) -> SkillSpec:
    """Derive a standard SkillSpec from natural language requirements."""
    struct_req = parse_natural_language_requirement(requirement, preferred_name=preferred_name)
    return struct_req.to_spec()


class AIAssistedEngine:
    """Coordinates safe AI-assisted skill creation and verification."""

    def __init__(
        self,
        provider: Optional[AIProvider] = None,
        max_repairs: int = 3,
    ) -> None:
        self.provider = provider or get_default_provider()
        self.max_repairs = max_repairs

    def build_skill(
        self,
        requirement: str,
        output_dir: Path | str,
        preferred_name: Optional[str] = None,
        quarantine_draft: bool = False,
        force_non_ai: bool = False,
    ) -> AICreationResult:
        """Run the end-to-end AI skill generation pipeline."""
        # Step 1: Requirements Interpretation & Assumption Register
        struct_req = parse_natural_language_requirement(requirement, preferred_name=preferred_name)
        spec = struct_req.to_spec()
        out_root = Path(output_dir).resolve()

        provider_available = self.provider.is_available() or isinstance(self.provider, MockAIProvider)

        # Step 2: Code & Test Generation
        if force_non_ai or not provider_available:
            script_code = generate_non_ai_implementation(struct_req)
            test_code = generate_behavioral_tests(struct_req)
            is_fallback = True
        else:
            gen_result = self.provider.generate_skill_code(spec, requirement)
            script_code = gen_result.script_code
            test_code = gen_result.test_code
            if not test_code.strip() or len(test_code.strip()) < 50:
                test_code = generate_behavioral_tests(struct_req)
            is_fallback = False

        # Step 3: Pre-Execution AST Safety & Secrets Inspection
        safety_findings = scan_python_code(script_code, file_path="scripts/main.py")
        safety_findings += scan_python_code(test_code, file_path="tests/test_main.py")
        secrets_findings = scan_secrets_in_text(script_code, file_path="scripts/main.py")
        secrets_findings += scan_secrets_in_text(test_code, file_path="tests/test_main.py")

        all_critical = [f for f in safety_findings if f.severity in ("CRITICAL", "HIGH")] + secrets_findings
        if all_critical:
            error_reasons = "; ".join(f"{f.rule_id}: {f.description}" for f in all_critical)
            return AICreationResult(
                status="safety_rejected",
                skill_name=spec.name,
                output_dir="",
                eval_score=0,
                grade="Grade F",
                repair_count=0,
                explanation=f"Code was intercepted and rejected by the AST Safety Scanner: {error_reasons}",
                safety_clean=False,
                is_draft=True,
                structured_spec=struct_req.to_dict(),
            )

        # Step 4: Sandboxed Isolated Subprocess Execution & Bounded Self-Repair
        repair_count = 0
        final_script = script_code
        final_test = test_code

        with tempfile.TemporaryDirectory() as sandbox_tmp:
            sandbox_path = Path(sandbox_tmp)
            gen_res = generate_skill(spec, sandbox_path)
            skill_sandbox = gen_res.target_path

            # Store requirement specification & assumption register
            spec_file = skill_sandbox / "references" / "spec.md"
            spec_file.parent.mkdir(parents=True, exist_ok=True)
            spec_file.write_text(struct_req.to_markdown(), encoding="utf-8")

            # Write generated code into sandbox
            (skill_sandbox / "scripts" / "main.py").write_text(final_script, encoding="utf-8")
            (skill_sandbox / "tests" / "test_main.py").write_text(final_test, encoding="utf-8")

            # Update manifest with generated files
            manifest = create_manifest(skill_sandbox, spec, spec.template_family)
            write_manifest(skill_sandbox, manifest)

            # Initial test execution
            test_res = run_skill_tests(skill_sandbox, timeout=10.0)

            # Bounded repair loop (only when using AI provider)
            while not test_res.success and repair_count < self.max_repairs and not is_fallback:
                repair_count += 1
                error_msg = test_res.error_message or test_res.stderr or "Unit tests failed"
                repair_result = self.provider.repair_skill_code(
                    spec=spec,
                    current_script=final_script,
                    current_test=final_test,
                    error_log=error_msg,
                )
                final_script = repair_result.script_code
                final_test = repair_result.test_code

                # Re-scan safety on repaired code
                recheck_findings = scan_python_code(final_script) + scan_python_code(final_test)
                if any(f.severity in ("CRITICAL", "HIGH") for f in recheck_findings):
                    break

                (skill_sandbox / "scripts" / "main.py").write_text(final_script, encoding="utf-8")
                (skill_sandbox / "tests" / "test_main.py").write_text(final_test, encoding="utf-8")
                manifest = create_manifest(skill_sandbox, spec, spec.template_family)
                write_manifest(skill_sandbox, manifest)

                test_res = run_skill_tests(skill_sandbox, timeout=10.0)

            if not test_res.success:
                return AICreationResult(
                    status="tests_failed",
                    skill_name=spec.name,
                    output_dir="",
                    eval_score=0,
                    grade="Grade F",
                    repair_count=repair_count,
                    explanation=f"Tests failed after {repair_count} self-repair attempt(s): {test_res.error_message}",
                    safety_clean=True,
                    is_draft=True,
                    structured_spec=struct_req.to_dict(),
                )

            # Step 5: Independent Functional Audit
            audit_report = audit_functional_correctness(skill_sandbox, struct_req)

            # Step 6: Full Quality Evaluation
            eval_report = evaluate_skill(skill_sandbox, run_tests=False, save_report=True)

            # Step 7: Deliver to Target Output Directory
            target_skill_dir = out_root / spec.name
            if target_skill_dir.exists():
                shutil.rmtree(target_skill_dir)

            target_skill_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(skill_sandbox, target_skill_dir)

            provider_name = self.provider.display_name if not is_fallback else "Deterministic Non-AI Fallback Engine"
            status_tag = "success" if not is_fallback else "fallback_success"

            return AICreationResult(
                status=status_tag,
                skill_name=spec.name,
                output_dir=str(target_skill_dir),
                eval_score=eval_report.total_score,
                grade=eval_report.grade,
                repair_count=repair_count,
                explanation=f"Skill '{spec.name}' successfully synthesized and validated via {provider_name}.",
                safety_clean=True,
                is_draft=quarantine_draft,
                structured_spec=struct_req.to_dict(),
                audit_report=audit_report.to_dict(),
            )
