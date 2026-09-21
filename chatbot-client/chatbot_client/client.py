from .exceptions import ChatbotResponseError
from .http_client import HTTPClient


class ChatbotClient:
    """High-level client for interacting with the chatbot API."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        max_retries: int = 0,
        retry_backoff_factor: float = 0.5,
    ):
        self.http_client = HTTPClient(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff_factor=retry_backoff_factor,
        )

    def create_chat(self, bot_id: str) -> str:
        """Create a new chatbot conversation and return its chat ID."""

        response = self.http_client.post(
            "/api/chats",
            {
                "botId": bot_id,
            },
        )

        chat_id = response.get("chatId")

        if not chat_id:
            raise ChatbotResponseError(
                "CreateChat response does not contain chatId."
            )

        return chat_id

    def send_message(
        self,
        chat_id: str,
        message: str,
        *,
        ignore_chat_history: bool = False,
        is_admin_chat: bool = False,
        trace_log_enabled: bool = False,
    ) -> str:
        """Send a message and return only the assistant's response."""

        response = self.http_client.post(
            f"/api/chats/{chat_id}/completions",
            {
                "userMessage": message,
                "ignoreChatHistory": ignore_chat_history,
                "isAdminChat": is_admin_chat,
                "isTraceLogEnabled": trace_log_enabled,
            },
        )

        assistant_message = response.get("assistantMessage")

        if assistant_message is None:
            raise ChatbotResponseError(
                "ChatCompletion response does not contain "
                "assistantMessage."
            )

        return assistant_message

    def close(self):
        """Close the underlying HTTP client."""

        self.http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()