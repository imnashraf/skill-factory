"""Skill Factory AI-Assisted Creation Module (Phase 15, Workstream E)."""
from __future__ import annotations

from skillfactory.ai.engine import AIAssistedEngine, AICreationResult, derive_spec_from_requirement
from skillfactory.ai.mock_provider import MockAIProvider
from skillfactory.ai.ollama import OllamaProvider
from skillfactory.ai.openai_compat import OpenAICompatibleProvider
from skillfactory.ai.provider import AIProvider, CodeGenerationResult

__all__ = [
    "AIProvider",
    "CodeGenerationResult",
    "MockAIProvider",
    "OllamaProvider",
    "OpenAICompatibleProvider",
    "AIAssistedEngine",
    "AICreationResult",
    "derive_spec_from_requirement",
]
