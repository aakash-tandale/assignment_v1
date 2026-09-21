class ChatbotError(Exception):
    """Base exception for all chatbot client errors."""


class ChatbotAPIError(ChatbotError):
    """Raised when the chatbot API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code


class ChatbotTimeoutError(ChatbotError):
    """Raised when a request to the chatbot API times out."""


class ChatbotResponseError(ChatbotError):
    """Raised when the chatbot API returns an unexpected response."""