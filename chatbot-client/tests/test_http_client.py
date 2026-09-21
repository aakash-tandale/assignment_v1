import httpx
import pytest

from chatbot_client.exceptions import ChatbotAPIError, ChatbotTimeoutError, ChatbotResponseError
from chatbot_client.http_client import HTTPClient
from unittest.mock import Mock, patch

def test_http_client_raises_error_for_http_failure():
    client = HTTPClient(
        base_url="http://test-server"
    )

    # Mock the underlying HTTP request.
    client.client.post = lambda *args, **kwargs: (
        httpx.Response(
            status_code=500,
            text="Internal Server Error",
        )
    )

    with pytest.raises(ChatbotAPIError) as exc_info:
      client.post(
        "/api/chats",
        {"botId": "test-bot"},
    )

    assert exc_info.value.status_code == 500


def test_http_client_raises_timeout_error():
    client = HTTPClient(
        base_url="http://test-server"
    )

    def raise_timeout(*args, **kwargs):
        raise httpx.TimeoutException(
            "Request timed out"
        )

    # Simulate a network timeout.
    client.client.post = raise_timeout

    with pytest.raises(ChatbotTimeoutError):
        client.post(
            "/api/chats",
            {"botId": "test-bot"},
        )


def test_http_client_raises_error_for_invalid_json():
    client = HTTPClient(
        base_url="http://test-server"
    )

    # Simulate a successful HTTP response
    # containing invalid JSON.
    client.client.post = lambda *args, **kwargs: (
        httpx.Response(
            status_code=200,
            content=b"this is not valid json",
        )
    )

    with pytest.raises(ChatbotResponseError):
        client.post(
            "/api/chats",
            {"botId": "test-bot"},
        )

@patch("chatbot_client.http_client.time.sleep")
def test_http_client_retries_on_server_error(mock_sleep):
    client = HTTPClient(
        base_url="http://test-server",
        max_retries=2,
    )

    responses = [
        httpx.Response(
            status_code=500,
            text="Internal Server Error",
        ),
        httpx.Response(
            status_code=500,
            text="Internal Server Error",
        ),
        httpx.Response(
            status_code=200,
            json={"chatId": "test-chat-id"},
        ),
    ]

    call_count = 0

    def mock_post(*args, **kwargs):
        nonlocal call_count

        response = responses[call_count]
        call_count += 1

        return response

    client.client.post = mock_post

    result = client.post(
        "/api/chats",
        {"botId": "test-bot"},
    )

    assert result == {
        "chatId": "test-chat-id"
    }

    assert call_count == 3
    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(0.5)
    mock_sleep.assert_any_call(1.0)

def test_http_client_stops_after_max_retries():
    client = HTTPClient(
        base_url="http://test-server",
        max_retries=2,
    )

    call_count = 0

    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1

        return httpx.Response(
            status_code=500,
            text="Internal Server Error",
        )

    client.client.post = mock_post

    with pytest.raises(ChatbotAPIError) as exc_info:
        client.post(
            "/api/chats",
            {"botId": "test-bot"},
        )

    # 1 initial attempt + 2 retries.
    assert call_count == 3

    assert exc_info.value.status_code == 500

@patch("chatbot_client.http_client.time.sleep")
def test_http_client_retries_on_timeout(mock_sleep):
    client = HTTPClient(
        base_url="http://test-server",
        max_retries=2,
    )

    call_count = 0

    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1

        if call_count < 3:
            raise httpx.TimeoutException(
                "Request timed out"
            )

        return httpx.Response(
            status_code=200,
            json={"chatId": "test-chat-id"},
        )

    client.client.post = mock_post

    result = client.post(
        "/api/chats",
        {"botId": "test-bot"},
    )

    assert result == {
        "chatId": "test-chat-id"
    }

    assert call_count == 3

    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(0.5)
    mock_sleep.assert_any_call(1.0)


def test_http_client_does_not_retry_client_error():
    client = HTTPClient(
        base_url="http://test-server",
        max_retries=2,
    )

    call_count = 0

    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1

        return httpx.Response(
            status_code=400,
            text="Bad Request",
        )

    client.client.post = mock_post

    with pytest.raises(ChatbotAPIError) as exc_info:
        client.post(
            "/api/chats",
            {"botId": "test-bot"},
        )

    assert call_count == 1
    assert exc_info.value.status_code == 400
