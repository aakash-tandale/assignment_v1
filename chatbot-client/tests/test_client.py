from unittest.mock import Mock

from chatbot_client import ChatbotClient
from chatbot_client.exceptions import ChatbotResponseError

def test_create_chat():
    # Mock the HTTP layer so this test does not call a real API.
    mock_http_client = Mock()

    # Tell the mock what the API should return.
    mock_http_client.post.return_value = {
        "chatId": "test-chat-id",
        "botId": "test-bot",
    }

    # Create our client.
    client = ChatbotClient(
        base_url="http://test-server"
    )

    # Replace the real HTTP client with our mock.
    client.http_client = mock_http_client

    # Call the method we want to test.
    chat_id = client.create_chat("test-bot")

    # Verify the returned value.
    assert chat_id == "test-chat-id"

    # Verify that the correct API request was made.
    mock_http_client.post.assert_called_once_with(
        "/api/chats",
        {
            "botId": "test-bot"
        },
    )


def test_send_message():
    # Mock the HTTP layer so we don't call the real API.
    mock_http_client = Mock()

    # Simulate the ChatCompletion API response.
    mock_http_client.post.return_value = {
        "chatId": "test-chat-id",
        "userMessage": "Hello",
        "assistantMessage": "Hello! How can I help you?",
    }

    client = ChatbotClient(
        base_url="http://test-server"
    )

    # Replace the real HTTP client with our mock.
    client.http_client = mock_http_client

    # Send a message.
    answer = client.send_message(
        "test-chat-id",
        "Hello",
    )

    # Verify that the client returns only assistantMessage.
    assert answer == "Hello! How can I help you?"

    # Verify the request sent to the API.
    mock_http_client.post.assert_called_once_with(
        "/api/chats/test-chat-id/completions",
        {
            "userMessage": "Hello",
            "ignoreChatHistory": False,
            "isAdminChat": False,
            "isTraceLogEnabled": False,
        },
    )
def test_create_chat_raises_error_when_chat_id_is_missing():
    # Mock the HTTP layer.
    mock_http_client = Mock()

    # Simulate an invalid API response.
    mock_http_client.post.return_value = {
        "botId": "test-bot"
    }

    client = ChatbotClient(
        base_url="http://test-server"
    )

    client.http_client = mock_http_client

    # Our client should reject the invalid response.
    try:
        client.create_chat("test-bot")
        assert False, "Expected ChatbotResponseError"
    except ChatbotResponseError:
        pass


def test_send_message_raises_error_when_assistant_message_is_missing():
    # Mock the HTTP layer.
    mock_http_client = Mock()

    # Simulate an invalid ChatCompletion response.
    mock_http_client.post.return_value = {
        "chatId": "test-chat-id",
        "userMessage": "Hello",
    }

    client = ChatbotClient(
        base_url="http://test-server"
    )

    client.http_client = mock_http_client

    # The client should reject the invalid response.
    try:
        client.send_message(
            "test-chat-id",
            "Hello",
        )
        assert False, "Expected ChatbotResponseError"
    except ChatbotResponseError:
        pass