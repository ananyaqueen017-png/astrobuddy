from abc import ABC, abstractmethod


class LLMError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code, self.message = status_code, message


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, user: str) -> str:
        """Return the model's text reply. Raise LLMError on provider failures."""
