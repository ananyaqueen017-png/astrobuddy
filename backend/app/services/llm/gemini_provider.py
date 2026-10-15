
from google import genai
from google.genai import types

from .base import LLMError, LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, timeout: float = 30.0):
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=int(timeout * 1000)
            ),
        )
        self._model = model

    def complete(self, system: str, user: str) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=user,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=1000,
                    response_mime_type="application/json",
                ),
            )
            text = response.text
            if not text:
                raise LLMError(
                    502, "The AI provider returned an empty response."
                )
            return text.strip()

        except LLMError:
            raise
        except Exception as e:
            # Do not expose API keys or raw provider error details.
            status = getattr(e, "code", None)
            if status == 429:
                raise LLMError(
                    503, "Gemini's usage limit was reached. Please try again later."
                )
            if status in (401, 403):
                raise LLMError(
                    502, "Gemini rejected the API credentials or access."
                )
            if "timeout" in type(e).__name__.lower():
                raise LLMError(
                    504, "The AI provider timed out. Please try again."
                )
            raise LLMError(
                502, "Gemini could not complete the request."
            )
