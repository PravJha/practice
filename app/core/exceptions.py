class LLMError(Exception):
    """Base class for all LLM-related errors."""


class LLMUnavailableError(LLMError):
    """Raised when the LLM backend is temporarily unavailable (retryable)."""


class ScrubbingError(Exception):
    """Raised when PII scrubbing fails unexpectedly."""
