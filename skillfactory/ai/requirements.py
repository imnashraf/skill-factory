"""Natural-Language Requirements Interpretation Engine (Phase 16, Workstream 16B).

Translates natural language user requests into a rigorous, structured specification:
- Business Objective
- Input & Output Contracts
- Validation Rules
- Edge Cases & Error Conditions
- Security Requirements
- Acceptance Criteria
- Explicit Assumption Register for ambiguous or unspecified business rules.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from skillfactory.spec import SkillSpec


@dataclass
class InputContract:
    """Defines an expected input for the skill."""
    name: str
    data_type: str
    format: str
    required: bool
    description: str


@dataclass
class OutputContract:
    """Defines an expected output from the skill."""
    name: str
    data_type: str
    format: str
    description: str


@dataclass
class ValidationRule:
    """Validation constraint on inputs or intermediate data."""
    field_name: str
    rule_type: str
    description: str
    error_action: str


@dataclass
class EdgeCase:
    """Boundary or abnormal condition."""
    scenario: str
    expected_behavior: str


@dataclass
class SecurityRequirement:
    """Security constraint for safe execution."""
    control_type: str
    description: str
    enforcement: str


@dataclass
class AcceptanceCriterion:
    """Acceptance criterion for behavioral verification."""
    criterion_id: str
    description: str
    test_scenario: str


@dataclass
class Assumption:
    """Explicitly recorded assumption for missing or ambiguous business rules."""
    category: str  # e.g., "Data Format", "Error Handling", "Scope", "Defaults"
    assumption_text: str
    rationale: str
    user_action_if_incorrect: str


@dataclass
class AssumptionRegister:
    """Registry of all explicit assumptions made during requirement interpretation."""
    items: List[Assumption] = field(default_factory=list)

    def add(self, category: str, text: str, rationale: str, user_action: str) -> None:
        self.items.append(
            Assumption(
                category=category,
                assumption_text=text,
                rationale=rationale,
                user_action_if_incorrect=user_action,
            )
        )

    def to_markdown(self) -> str:
        if not self.items:
            return "No assumptions recorded (specification fully determined)."
        lines = [
            "| # | Category | Assumption | Rationale | Remediation If Incorrect |",
            "|---|---|---|---|---|",
        ]
        for idx, item in enumerate(self.items, 1):
            lines.append(
                f"| {idx} | {item.category} | {item.assumption_text} | {item.rationale} | {item.user_action_if_incorrect} |"
            )
        return "\n".join(lines)

    def to_list(self) -> List[Dict[str, Any]]:
        return [asdict(a) for a in self.items]


@dataclass
class StructuredRequirementSpec:
    """Comprehensive, machine-readable specification derived from natural language."""
    skill_name: str
    business_objective: str
    domain: str
    category: str
    inputs: List[InputContract]
    outputs: List[OutputContract]
    validation_rules: List[ValidationRule]
    edge_cases: List[EdgeCase]
    error_conditions: List[str]
    security_requirements: List[SecurityRequirement]
    acceptance_criteria: List[AcceptanceCriterion]
    assumption_register: AssumptionRegister

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["assumption_register"] = self.assumption_register.to_list()
        return data

    def to_spec(self, author: str = "Skill Factory Requirements Engine") -> SkillSpec:
        """Convert structured requirements into a standard SkillSpec."""
        desc = self.business_objective if len(self.business_objective) <= 200 else self.business_objective[:197] + "..."
        return SkillSpec(
            name=self.skill_name,
            description=desc,
            template_family="python-script",
            author=author,
            license="MIT",
        )

    def to_markdown(self) -> str:
        """Render the structured specification as Markdown."""
        lines = [
            f"# Specification: {self.skill_name}",
            "",
            f"**Objective**: {self.business_objective}",
            f"**Domain**: {self.domain} | **Category**: {self.category}",
            "",
            "## 1. Input Contracts",
            "| Name | Type | Format | Required | Description |",
            "|---|---|---|---|---|",
        ]
        for inp in self.inputs:
            lines.append(f"| {inp.name} | {inp.data_type} | {inp.format} | {'Yes' if inp.required else 'No'} | {inp.description} |")

        lines.extend([
            "",
            "## 2. Output Contracts",
            "| Name | Type | Format | Description |",
            "|---|---|---|---|",
        ])
        for out in self.outputs:
            lines.append(f"| {out.name} | {out.data_type} | {out.format} | {out.description} |")

        lines.extend([
            "",
            "## 3. Validation Rules",
            "| Field | Rule Type | Description | On Error |",
            "|---|---|---|---|",
        ])
        for rule in self.validation_rules:
            lines.append(f"| {rule.field_name} | {rule.rule_type} | {rule.description} | {rule.error_action} |")

        lines.extend([
            "",
            "## 4. Edge Cases",
            "| Scenario | Expected Behavior |",
            "|---|---|",
        ])
        for edge in self.edge_cases:
            lines.append(f"| {edge.scenario} | {edge.expected_behavior} |")

        lines.extend([
            "",
            "## 5. Security Requirements",
            "| Control | Description | Enforcement |",
            "|---|---|---|",
        ])
        for sec in self.security_requirements:
            lines.append(f"| {sec.control_type} | {sec.description} | {sec.enforcement} |")

        lines.extend([
            "",
            "## 6. Acceptance Criteria",
            "| ID | Criterion | Test Scenario |",
            "|---|---|---|",
        ])
        for ac in self.acceptance_criteria:
            lines.append(f"| {ac.criterion_id} | {ac.description} | {ac.test_scenario} |")

        lines.extend([
            "",
            "## 7. Assumption Register",
            self.assumption_register.to_markdown(),
            "",
        ])
        return "\n".join(lines)


def _derive_name(requirement: str, preferred_name: Optional[str] = None) -> str:
    if preferred_name:
        name = preferred_name
    else:
        words = re.findall(r"[A-Za-z0-9]+", requirement)
        stopwords = {
            "create", "skill", "that", "with", "from", "into", "this", "tool",
            "agent", "please", "make", "build", "write", "generate", "does", "will"
        }
        meaningful = [w.lower() for w in words if len(w) > 2 and w.lower() not in stopwords]
        name = "-".join(meaningful[:3]) if meaningful else "agent-skill"

    sanitized = re.sub(r"[^a-z0-9\-]", "", name.lower().replace("_", "-").replace(" ", "-")).strip("-")
    return sanitized or "agent-skill"


def parse_natural_language_requirement(
    requirement: str,
    preferred_name: Optional[str] = None,
) -> StructuredRequirementSpec:
    """Parse natural language into a rich structured specification with an Assumption Register.

    Analyzes intent, entities, formats, constraints, and business logic.
    Identifies ambiguities and explicitly records assumptions rather than guessing blindly.
    """
    clean_req = requirement.strip()
    skill_name = _derive_name(clean_req, preferred_name)
    lower_req = clean_req.lower()

    assumptions = AssumptionRegister()

    # Domain classification
    domain = "Developer"
    category = "Utilities"
    if any(k in lower_req for k in ("invoice", "financial", "attendance", "payroll", "budget", "ledger", "tax")):
        domain = "Professional"
        category = "Finance & Workforce"
    elif any(k in lower_req for k in ("raid", "project", "milestone", "agile", "sprint", "task", "status")):
        domain = "Professional"
        category = "Project Management"
    elif any(k in lower_req for k in ("excel", "csv", "table", "sheet", "diff", "compare", "file", "notes")):
        domain = "Personal"
        category = "Productivity"
    elif any(k in lower_req for k in ("security", "scanner", "vuln", "ast", "dependency", "test", "docker")):
        domain = "Developer"
        category = "DevOps & Security"

    inputs: List[InputContract] = []
    outputs: List[OutputContract] = []
    validation_rules: List[ValidationRule] = []
    edge_cases: List[EdgeCase] = []
    error_conditions: List[str] = []
    security_requirements: List[SecurityRequirement] = []
    acceptance_criteria: List[AcceptanceCriterion] = []

    # Common security requirements across all skills
    security_requirements.append(
        SecurityRequirement(
            control_type="Path Traversal Defense",
            description="Input and output paths must be resolved and checked against directory escape.",
            enforcement="Reject paths containing '..' escaping working root with exit code 2.",
        )
    )
    security_requirements.append(
        SecurityRequirement(
            control_type="File Size Limiting",
            description="Prevent memory exhaustion / denial-of-service on unbounded input files.",
            enforcement="Reject individual files exceeding 25MB with exit code 2.",
        )
    )

    # Heuristic parsing for common patterns
    if "excel" in lower_req or "diff" in lower_req or "compare" in lower_req:
        # Excel comparison / Diff pattern
        inputs.append(
            InputContract(
                name="file_a",
                data_type="file_path",
                format="csv/tsv/table",
                required=True,
                description="Primary baseline table file.",
            )
        )
        inputs.append(
            InputContract(
                name="file_b",
                data_type="file_path",
                format="csv/tsv/table",
                required=True,
                description="Comparison target table file.",
            )
        )
        outputs.append(
            OutputContract(
                name="difference_report",
                data_type="file_path/stdout",
                format="markdown/text",
                description="Detailed summary of added, removed, and modified rows/cells.",
            )
        )
        validation_rules.append(
            ValidationRule(
                field_name="file_a, file_b",
                rule_type="File Existence",
                description="Both files must exist and be readable.",
                error_action="Exit code 1 with descriptive missing file message.",
            )
        )
        validation_rules.append(
            ValidationRule(
                field_name="header_alignment",
                rule_type="Schema Consistency",
                description="Columns in both files should have compatible keys.",
                error_action="Flag missing columns in comparison report.",
            )
        )
        edge_cases.append(EdgeCase("Identical files", "Report zero differences and exit code 0."))
        edge_cases.append(EdgeCase("Empty file", "Report error if either file is 0 bytes."))
        edge_cases.append(EdgeCase("Reordered rows", "Compare rows by primary key or line hash."))

        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-1",
                description="Detect modified cell values across files.",
                test_scenario="Pass two files with one cell changed; verify diff report identifies line & column.",
            )
        )
        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-2",
                description="Handle identical files cleanly.",
                test_scenario="Pass identical files; report must state files are identical with exit code 0.",
            )
        )
        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-3",
                description="Graceful error on missing input files.",
                test_scenario="Pass non-existent file path; exit code must be non-zero without unhandled crash.",
            )
        )

        assumptions.add(
            category="Data Format",
            text="Assumed standard tabular text format (CSV/TSV/delimited) if binary .xlsx is not directly specified.",
            rationale="Maintains 100% Python standard library compatibility without third-party openpyxl.",
            user_action="Specify CSV format or provide converted CSV export.",
        )
        assumptions.add(
            category="Comparison Key",
            text="Assumed first column acts as primary row key unless row-by-row line comparison is requested.",
            rationale="Allows robust diffing even if rows are permuted.",
            user_action="Provide explicit '--key' parameter in script arguments if different column is key.",
        )

    elif "attendance" in lower_req or "employee" in lower_req:
        # Attendance validation pattern
        inputs.append(
            InputContract(
                name="attendance_csv",
                data_type="file_path",
                format="csv",
                required=True,
                description="Employee attendance log CSV.",
            )
        )
        outputs.append(
            OutputContract(
                name="validation_summary",
                data_type="stdout/json",
                format="json/text",
                description="Count of valid, missing, or irregular attendance records.",
            )
        )
        validation_rules.append(
            ValidationRule(
                field_name="employee_id",
                rule_type="Non-Empty",
                description="Employee ID must not be blank.",
                error_action="Flag record as invalid.",
            )
        )
        validation_rules.append(
            ValidationRule(
                field_name="timestamp",
                rule_type="ISO Date / Time Format",
                description="Timestamps must adhere to standard date/time representation.",
                error_action="Flag invalid format.",
            )
        )
        edge_cases.append(EdgeCase("Missing check-out time", "Flag as incomplete shift record."))
        edge_cases.append(EdgeCase("Duplicate employee check-in on same day", "Flag as duplicate punch."))

        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-1",
                description="Validate properly formatted attendance CSV.",
                test_scenario="Provide valid employee rows; report valid count.",
            )
        )
        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-2",
                description="Flag missing employee ID or invalid dates.",
                test_scenario="Provide row with blank employee ID; verify violation is reported.",
            )
        )

        assumptions.add(
            category="Date Format",
            text="Assumed dates are in ISO-8601 (YYYY-MM-DD) format.",
            rationale="Standard international date interchange format.",
            user_action="Specify custom date format string in settings if DD/MM/YYYY is required.",
        )
        assumptions.add(
            category="Working Hours",
            text="Assumed shifts longer than 16 hours or shorter than 1 hour require review flags.",
            rationale="Standard occupational health boundary rules.",
            user_action="Adjust threshold parameters in script configuration.",
        )

    elif "raid" in lower_req or "risk" in lower_req or "project" in lower_req:
        # RAID log review pattern
        inputs.append(
            InputContract(
                name="raid_log",
                data_type="file_path",
                format="csv/markdown",
                required=True,
                description="Project RAID (Risks, Assumptions, Issues, Dependencies) log.",
            )
        )
        outputs.append(
            OutputContract(
                name="audit_report",
                data_type="markdown",
                format="markdown",
                description="Project risk severity matrix and hygiene report.",
            )
        )
        validation_rules.append(
            ValidationRule(
                field_name="item_type",
                rule_type="Enum [Risk, Assumption, Issue, Dependency]",
                description="Type must be one of the four RAID pillars.",
                error_action="Flag unclassified item.",
            )
        )
        validation_rules.append(
            ValidationRule(
                field_name="owner",
                rule_type="Non-Empty",
                description="Every RAID item must have an assigned owner.",
                error_action="Flag unassigned item.",
            )
        )
        edge_cases.append(EdgeCase("All items resolved/closed", "Report 100% resolution health."))
        edge_cases.append(EdgeCase("Critical severity with past-due date", "Elevate to red project alert."))

        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-1",
                description="Parse valid RAID entries.",
                test_scenario="Parse CSV containing Risks and Issues; verify correct tallying.",
            )
        )
        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-2",
                description="Flag unassigned critical risks.",
                test_scenario="Provide Critical risk without owner; verify warning in audit report.",
            )
        )

        assumptions.add(
            category="Severity Scale",
            text="Assumed severity uses 3-tier scale: High / Medium / Low.",
            rationale="Most common industry RAID log convention.",
            user_action="Configure custom scoring weights in script if 5x5 matrix is used.",
        )
        assumptions.add(
            category="Ownership",
            text="Assumed unassigned items are flagged as high governance risks.",
            rationale="Accountability requirement for enterprise project audits.",
            user_action="Mark items as 'Unassigned - TBD' if intentional.",
        )

    elif "invoice" in lower_req:
        # Invoice reconciliation pattern
        inputs.append(
            InputContract(
                name="invoices_file",
                data_type="file_path",
                format="csv/json",
                required=True,
                description="List of vendor invoices and billing items.",
            )
        )
        outputs.append(
            OutputContract(
                name="reconciliation_report",
                data_type="json/markdown",
                format="json/markdown",
                description="Reconciliation report detailing matched, mismatched, and duplicate invoices.",
            )
        )
        validation_rules.append(
            ValidationRule(
                field_name="invoice_number",
                rule_type="Unique Identifier",
                description="Invoice numbers must be present.",
                error_action="Flag invalid invoice row.",
            )
        )
        validation_rules.append(
            ValidationRule(
                field_name="amount",
                rule_type="Positive Float",
                description="Invoice amount must be non-negative numeric value.",
                error_action="Flag invalid currency or amount.",
            )
        )
        edge_cases.append(EdgeCase("Duplicate invoice numbers", "Flag potential double-billing."))
        edge_cases.append(EdgeCase("Rounding differences (< $0.05)", "Classify as acceptable rounding variance."))

        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-1",
                description="Detect duplicate invoice numbers.",
                test_scenario="Input file with duplicate invoice #1001; verify report lists duplicate.",
            )
        )
        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-2",
                description="Verify positive amount calculations.",
                test_scenario="Input invalid negative amount; verify error flag in report.",
            )
        )

        assumptions.add(
            category="Currency",
            text="Assumed currency is USD unless explicit currency symbols/codes are present.",
            rationale="Standard default for automated financial parsing.",
            user_action="Add currency column to invoice dataset.",
        )
        assumptions.add(
            category="Tolerance",
            text="Assumed reconciliation tolerance threshold is $0.01.",
            rationale="Standard penny-rounding tolerance.",
            user_action="Specify custom tolerance parameter via CLI.",
        )

    else:
        # General / Custom Agent Skill Pattern
        inputs.append(
            InputContract(
                name="input_target",
                data_type="file_path/text",
                format="text/json/csv",
                required=True,
                description="Primary data or file input for the skill.",
            )
        )
        outputs.append(
            OutputContract(
                name="result_output",
                data_type="stdout/file",
                format="text/json",
                description="Structured output or summary result.",
            )
        )
        validation_rules.append(
            ValidationRule(
                field_name="input_target",
                rule_type="Presence & Readability",
                description="Target input must be supplied and accessible.",
                error_action="Exit code 2 with usage instructions.",
            )
        )
        edge_cases.append(EdgeCase("Empty input", "Display clear warning and exit safely."))
        edge_cases.append(EdgeCase("Malformed format", "Report specific parsing error line."))

        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-1",
                description="Execute core skill workflow successfully.",
                test_scenario="Run script with sample input; verify expected output and exit code 0.",
            )
        )
        acceptance_criteria.append(
            AcceptanceCriterion(
                criterion_id="AC-2",
                description="Handle missing arguments gracefully.",
                test_scenario="Run script with no arguments; verify friendly usage message and exit code 2.",
            )
        )

        assumptions.add(
            category="Execution Environment",
            text="Assumed script runs under Python 3.9+ standard library without external pip packages.",
            rationale="Skill Factory zero-dependency core requirement.",
            user_action="Specify dependencies in requirements.txt if optional external packages are needed.",
        )
        assumptions.add(
            category="Input Encoding",
            text="Assumed text files use UTF-8 character encoding.",
            rationale="Universal cross-platform standard.",
            user_action="Provide encoding flag if legacy encodings (e.g. latin-1, cp1252) are used.",
        )

    error_conditions.extend([
        "Missing required arguments or input files -> Exit Code 2 (Argument Error)",
        "Malformed data or schema failure -> Exit Code 1 (Validation Error)",
        "Path traversal attempt or file over 25MB -> Exit Code 2 (Security Rejection)",
    ])

    return StructuredRequirementSpec(
        skill_name=skill_name,
        business_objective=clean_req,
        domain=domain,
        category=category,
        inputs=inputs,
        outputs=outputs,
        validation_rules=validation_rules,
        edge_cases=edge_cases,
        error_conditions=error_conditions,
        security_requirements=security_requirements,
        acceptance_criteria=acceptance_criteria,
        assumption_register=assumptions,
    )
