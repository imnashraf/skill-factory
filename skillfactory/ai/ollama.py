"""Local Ollama AI Provider (Phase 15, Workstream E).

Zero cloud dependencies, zero external costs, 100% local inference.
Connects to local Ollama daemon via http://localhost:11434.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from skillfactory.ai.provider import AIProvider, CodeGenerationResult
from skillfactory.spec import SkillSpec


class OllamaProvider(AIProvider):
    """Local inference provider using Ollama daemon."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = (base_url or os.environ.get("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL") or "llama3"
        self.timeout = timeout

    @property
    def provider_id(self) -> str:
        return "ollama"

    @property
    def display_name(self) -> str:
        return f"Local Ollama ({self.model} @ {self.base_url})"

    def is_available(self) -> bool:
        """Check if local Ollama daemon is active and responding."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", headers={"User-Agent": "SkillFactory/1.5"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _query_ollama(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "SkillFactory/1.5"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("response", "")

    def generate_skill_code(
        self,
        spec: SkillSpec,
        prompt: str,
    ) -> CodeGenerationResult:
        system_prompt = (
            f"You are a Python expert creating an Agent Skill named '{spec.name}'.\n"
            f"Description: {spec.description}\n"
            f"User Requirement: {prompt}\n\n"
            "Generate two valid Python files formatted as JSON:\n"
            "{\n"
            '  "script_code": "Complete Python script for scripts/main.py (use standard library only)",\n'
            '  "test_code": "Complete unittest suite for tests/test_main.py"\n'
            "}\n"
            "Do NOT include shell=True or eval. Ensure code is safe and deterministic."
        )

        raw = self._query_ollama(system_prompt)
        try:
            parsed = json.loads(raw)
            return CodeGenerationResult(
                script_code=parsed.get("script_code", ""),
                test_code=parsed.get("test_code", ""),
                explanation=f"Generated via Ollama {self.model}",
                raw_response=parsed,
            )
        except Exception:
            # Fallback if markdown fences wrapped the JSON
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                parsed = json.loads(m.group(0))
                return CodeGenerationResult(
                    script_code=parsed.get("script_code", ""),
                    test_code=parsed.get("test_code", ""),
                    explanation=f"Generated via Ollama {self.model}",
                )
            raise ValueError(f"Ollama returned non-JSON response: {raw[:200]}")

    def repair_skill_code(
        self,
        spec: SkillSpec,
        current_script: str,
        current_test: str,
        error_log: str,
    ) -> CodeGenerationResult:
        repair_prompt = (
            f"The Python script or test for skill '{spec.name}' failed with errors:\n"
            f"--- ERROR LOG ---\n{error_log}\n-----------------\n\n"
            f"Current scripts/main.py:\n{current_script}\n\n"
            f"Current tests/test_main.py:\n{current_test}\n\n"
            "Fix the bug and return valid JSON with keys 'script_code' and 'test_code'."
        )
        raw = self._query_ollama(repair_prompt)
        parsed = json.loads(raw)
        return CodeGenerationResult(
            script_code=parsed.get("script_code", current_script),
            test_code=parsed.get("test_code", current_test),
            explanation=f"Repaired via Ollama {self.model}",
        )
