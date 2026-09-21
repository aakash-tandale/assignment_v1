import time

import httpx

from .exceptions import (
    ChatbotAPIError,
    ChatbotResponseError,
    ChatbotTimeoutError,
)


class HTTPClient:
    """Low-level HTTP client used by ChatbotClient."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        max_retries: int = 0,
        retry_backoff_factor: float = 0.5,
    ):
        if not base_url:
            raise ValueError("base_url cannot be empty.")

        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

        if retry_backoff_factor < 0:
            raise ValueError(
                "retry_backoff_factor cannot be negative."
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor

        self.client = httpx.Client(
            timeout=self.timeout,
        )

    def close(self):
        """Close the underlying HTTP client."""

        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _is_retryable_status(self, status_code: int) -> bool:
        """Return whether an HTTP status represents a transient server error."""

        return 500 <= status_code < 600

    def _sleep_before_retry(self, attempt: int):
        """Apply exponential backoff before the next retry."""

        delay = self.retry_backoff_factor * (2**attempt)
        time.sleep(delay)

    def post(
        self,
        path: str,
        json: dict,
    ) -> dict:
        """Send a POST request and return the decoded JSON response."""

        url = f"{self.base_url}{path}"

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.post(
                    url,
                    json=json,
                )

            except httpx.TimeoutException as exc:
                if attempt < self.max_retries:
                    self._sleep_before_retry(attempt)
                    continue

                raise ChatbotTimeoutError(
                    f"Request to {path} timed out."
                ) from exc

            except httpx.RequestError as exc:
                raise ChatbotAPIError(
                    f"Failed to communicate with chatbot API: {exc}"
                ) from exc

            if response.is_error:
                if (
                    self._is_retryable_status(response.status_code)
                    and attempt < self.max_retries
                ):
                    self._sleep_before_retry(attempt)
                    continue

                raise ChatbotAPIError(
                    f"Chatbot API returned HTTP "
                    f"{response.status_code}: {response.text}",
                    status_code=response.status_code,
                )

            try:
                return response.json()

            except ValueError as exc:
                raise ChatbotResponseError(
                    "Chatbot API returned invalid JSON."
                ) from exc

        raise ChatbotAPIError(
            "Request failed after all retry attempts."
        )