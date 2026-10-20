"""OpenAI-Compatible Local AI Provider (Phase 15, Workstream E).

Connects to any standard /v1/chat/completions endpoint (e.g. vLLM, LM Studio, LocalAI)
using pure Python standard library (urllib.request).
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


class OpenAICompatibleProvider(AIProvider):
    """Provider connecting to standard /v1/chat/completions endpoints."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "http://localhost:8000/v1").rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or "local-key"
        self.model = model or os.environ.get("OPENAI_MODEL") or "default-model"
        self.timeout = timeout

    @property
    def provider_id(self) -> str:
        return "openai-compat"

    @property
    def display_name(self) -> str:
        return f"OpenAI-Compatible ({self.model} @ {self.base_url})"

    def is_available(self) -> bool:
        """Check if endpoint is reachable."""
        try:
            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}", "User-Agent": "SkillFactory/1.5"},
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _call_completions(self, messages: list) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "SkillFactory/1.5",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            choices = body.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""

    def generate_skill_code(
        self,
        spec: SkillSpec,
        prompt: str,
    ) -> CodeGenerationResult:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Senior Python Engineer generating an Agent Skill.\n"
                    "Return ONLY valid JSON with keys 'script_code' (for scripts/main.py) "
                    "and 'test_code' (for tests/test_main.py). Use only Python standard library."
                ),
            },
            {
                "role": "user",
                "content": f"Skill: {spec.name}\nDescription: {spec.description}\nRequirement: {prompt}",
            },
        ]
        raw = self._call_completions(messages)
        try:
            parsed = json.loads(raw)
        except Exception:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                parsed = json.loads(m.group(0))
            else:
                raise ValueError(f"Failed to parse JSON response: {raw[:200]}")

        return CodeGenerationResult(
            script_code=parsed.get("script_code", ""),
            test_code=parsed.get("test_code", ""),
            explanation="Generated via OpenAI-compatible endpoint",
        )

    def repair_skill_code(
        self,
        spec: SkillSpec,
        current_script: str,
        current_test: str,
        error_log: str,
    ) -> CodeGenerationResult:
        messages = [
            {
                "role": "system",
                "content": "You are a code repair assistant. Fix the failing test or script and return JSON with keys 'script_code' and 'test_code'.",
            },
            {
                "role": "user",
                "content": f"Errors:\n{error_log}\n\nScript:\n{current_script}\n\nTest:\n{current_test}",
            },
        ]
        raw = self._call_completions(messages)
        parsed = json.loads(raw)
        return CodeGenerationResult(
            script_code=parsed.get("script_code", current_script),
            test_code=parsed.get("test_code", current_test),
            explanation="Repaired via OpenAI-compatible endpoint",
        )
