"""Skill Factory AI-Assisted Creation Module (Phases 15 & 16)."""
from __future__ import annotations

from skillfactory.ai.engine import AIAssistedEngine, AICreationResult, derive_spec_from_requirement
from skillfactory.ai.evaluator import (
    FunctionalAuditReport,
    TraceabilityEntry,
    audit_functional_correctness,
    generate_non_ai_implementation,
)
from skillfactory.ai.mock_provider import MockAIProvider
from skillfactory.ai.ollama import OllamaProvider
from skillfactory.ai.openai_compat import OpenAICompatibleProvider
from skillfactory.ai.provider import AIProvider, CodeGenerationResult
from skillfactory.ai.requirements import (
    AcceptanceCriterion,
    Assumption,
    AssumptionRegister,
    InputContract,
    OutputContract,
    StructuredRequirementSpec,
    parse_natural_language_requirement,
)
from skillfactory.ai.test_gen import generate_behavioral_tests

__all__ = [
    "AIProvider",
    "CodeGenerationResult",
    "MockAIProvider",
    "OllamaProvider",
    "OpenAICompatibleProvider",
    "AIAssistedEngine",
    "AICreationResult",
    "derive_spec_from_requirement",
    "StructuredRequirementSpec",
    "AssumptionRegister",
    "Assumption",
    "InputContract",
    "OutputContract",
    "AcceptanceCriterion",
    "parse_natural_language_requirement",
    "generate_behavioral_tests",
    "audit_functional_correctness",
    "generate_non_ai_implementation",
    "FunctionalAuditReport",
    "TraceabilityEntry",
]
