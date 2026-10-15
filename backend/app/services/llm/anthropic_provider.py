import httpx

from .base import LLMError, LLMProvider

_URL = "https://api.anthropic.com/v1/messages"


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, timeout: float = 30.0):
        self._key, self._model, self._timeout = api_key, model, timeout

    def complete(self, system: str, user: str) -> str:
        try:
            r = httpx.post(
                _URL, timeout=self._timeout,
                headers={"x-api-key": self._key, "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                json={"model": self._model, "max_tokens": 1000, "system": system,
                      "messages": [{"role": "user", "content": user}]},
            )
        except httpx.TimeoutException:
            raise LLMError(504, "The AI provider timed out. Please try again.")
        except httpx.HTTPError:
            raise LLMError(502, "Could not reach the AI provider.")
        if r.status_code >= 400:  # never forward the provider's body (may echo request details)
            raise LLMError(502, f"The AI provider returned an error (HTTP {r.status_code}).")
        try:
            blocks = r.json().get("content", [])
            return "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
        except ValueError:
            raise LLMError(502, "The AI provider returned an unreadable response.")
