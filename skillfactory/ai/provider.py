"""Abstract base class and models for AI providers (Phase 15, Workstream E).

Zero mandatory cloud dependencies. Pluggable architecture supporting local inference
(Ollama, local vLLM, LM Studio) and offline test mocks.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from skillfactory.spec import SkillSpec


@dataclass
class CodeGenerationResult:
    """Output of AI code generation."""
    script_code: str
    test_code: str
    explanation: str = ""
    raw_response: Optional[Dict[str, Any]] = None


class AIProvider(ABC):
    """Abstract interface for local or remote AI code generation providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available for inference."""
        pass

    @abstractmethod
    def generate_skill_code(
        self,
        spec: SkillSpec,
        prompt: str,
    ) -> CodeGenerationResult:
        """Generate functional script and unit test implementation."""
        pass

    @abstractmethod
    def repair_skill_code(
        self,
        spec: SkillSpec,
        current_script: str,
        current_test: str,
        error_log: str,
    ) -> CodeGenerationResult:
        """Attempt bounded self-repair on failing script or test."""
        pass
