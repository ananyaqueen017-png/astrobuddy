
from typing import Optional

from app.core.config import Settings
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider
from .base import LLMProvider


def build_provider(s: Settings) -> Optional[LLMProvider]:
    """Return a configured AI provider, or None when disabled."""

    if s.llm_provider.lower() == "gemini":
        if s.gemini_api_key and s.llm_model:
            return GeminiProvider(
                s.gemini_api_key,
                s.llm_model,
                s.llm_timeout_seconds,
            )
        return None

    if s.llm_provider.lower() == "anthropic":
        if s.anthropic_api_key and s.llm_model:
            return AnthropicProvider(
                s.anthropic_api_key,
                s.llm_model,
                s.llm_timeout_seconds,
            )
        return None

    return None
