# Chatbot Client

A reusable Python client for interacting with the AI Chatbot REST API.

The client provides a simple interface for:

- Creating a chat
- Sending messages to an existing chat
- Returning the assistant response
- Handling API errors and timeouts
- Validating API responses
- Optionally retrying transient failures

## Requirements

- Python 3.10+
- Access to the chatbot API

## Installation

Install the package from the project root:

```
pip install .
```

The package installs httpx as its runtime dependency.

## Quick Start

```
from chatbot_client import ChatbotClient


with ChatbotClient(
    base_url="https://chatbot.example.com"
) as client:

    chat_id = client.create_chat("my-bot")

    answer = client.send_message(
        chat_id,
        "Hello, how are you?"
    )

    print(answer)
```

The consumer only needs to work with ChatbotClient. The underlying HTTP requests, request payloads, response parsing, and error handling are handled internally by the module.

## API Operations



### Create Chat

The client calls:

```
POST /api/chats
```

and returns the generated chatId.

Example:

```
chat_id = client.create_chat("my-bot")
```



### Send Message

The client calls:

```
POST /api/chats/{chatId}/completions
```

and returns only assistantMessage from the API response.

Example:

```
answer = client.send_message(
    chat_id,
    "What can you help me with?"
)
```

Optional request flags are also supported:

```
answer = client.send_message(
    chat_id,
    "Hello",
    ignore_chat_history=False,
    is_admin_chat=False,
    trace_log_enabled=False,
)
```



## Configuration

The client supports the following configuration:

```
ChatbotClient(
    base_url="https://chatbot.example.com",
    timeout=10.0,
    max_retries=0,
    retry_backoff_factor=0.5,
)
```



### base_url

The base URL of the chatbot API.

It is configurable so the same client can be used with different environments.

### timeout

Request timeout in seconds.

Default: 10 seconds.

### max_retries

Maximum number of retries for transient failures.

Default: 0.

Retries are disabled by default.

### retry_backoff_factor

Controls the exponential backoff between retries.

Default: 0.5 seconds.

## Retry Behavior

The client retries only transient failures:

- HTTP 5xx responses
- Request timeouts

HTTP 4xx responses are not retried.

For example:

```
with ChatbotClient(
    base_url="https://chatbot.example.com",
    max_retries=2,
) as client:

    chat_id = client.create_chat("my-bot")
    answer = client.send_message(
        chat_id,
        "Hello"
    )
```

With max_retries=2, the client can make up to three attempts:

```
Initial request
      |
      | failure
      v
Retry 1
      |
      | failure
      v
Retry 2
```

Retries are disabled by default.

Because the provided API contract does not define an idempotency-key mechanism, retries should only be enabled when the consumer is comfortable retrying the underlying operation.

## Error Handling

The client exposes specific exceptions:

```
from chatbot_client.exceptions import (
    ChatbotAPIError,
    ChatbotTimeoutError,
    ChatbotResponseError,
)
```



### ChatbotAPIError

Raised when the chatbot API returns an HTTP error or when the request cannot be completed.

For HTTP responses, the exception exposes the HTTP status code when available.

Example:

```
try:
    ...
except ChatbotAPIError as error:
    print(error.status_code)
```



### ChatbotTimeoutError

Raised when a request to the chatbot API times out.

### ChatbotResponseError

Raised when the API returns an unexpected response, such as:

- Invalid JSON
- Missing chatId from CreateChat
- Missing assistantMessage from ChatCompletion



## Mock Server

The repository contains a small FastAPI mock server for local development and testing.

The mock server is NOT the real chatbot backend. It implements only the API operations required for this assignment.

Start the mock server with:

```
uvicorn mock_server.app:app --reload
```

The mock server implements:

```
POST /api/chats
POST /api/chats/{chatId}/completions
```

Once the mock server is running, execute the example from the project root:

```
python3 -m examples.basic_usage
```

Example output:

```
Created chat: <chat-id>
Assistant: Mock response for: Hello, how are you?
```



## Testing

Run the complete test suite with:

```
python3 -m pytest -v
```

The tests cover:

- Successful chat creation
- Successful message completion
- Missing chatId
- Missing assistantMessage
- HTTP errors
- Request timeouts
- Invalid JSON responses
- Retry behavior
- Retry limits
- Non-retryable HTTP 4xx responses
- Exponential backoff

The tests mock the underlying HTTP calls, so they do not require the real chatbot API.

## Project Structure

```
chatbot-client/
|
+-- chatbot_client/
|   +-- __init__.py
|   +-- client.py
|   +-- http_client.py
|   +-- exceptions.py
|
+-- examples/
|   +-- basic_usage.py
|
+-- mock_server/
|   +-- app.py
|
+-- tests/
|   +-- test_client.py
|   +-- test_http_client.py
|
+-- pyproject.toml
+-- README.md
```



### Module Responsibilities

ChatbotClient

Provides the high-level interface used by consuming applications.

HTTPClient

Handles HTTP communication, timeouts, API errors, response parsing, and retry behavior.

exceptions.py

Defines the exceptions exposed by the client.

mock_server

Provides a local mock implementation of the required chatbot API operations.

tests

Contains unit tests for the client and HTTP behavior.

## API Contract

The implementation follows the provided OpenAPI specification for the following operations:

```
CreateChat
POST /api/chats

ChatCompletion
POST /api/chats/{chatId}/completions
```

The CreateChat request uses:

```
{
    "botId": "string"
}
```

The ChatCompletion request uses:

```
{
    "userMessage": "string",
    "ignoreChatHistory": false,
    "isAdminChat": false,
    "isTraceLogEnabled": false
}
```

The consumer-facing module returns:

- chatId from CreateChat
- assistantMessage from ChatCompletion



## Assumptions

The provided API contract does not specify an authentication mechanism. Authentication is therefore not implemented or assumed by this client.

The included FastAPI server is a local mock used only for development and demonstration.

## Example Consumer Flow

```
from chatbot_client import ChatbotClient


with ChatbotClient(
    base_url="https://chatbot.example.com"
) as client:

    chat_id = client.create_chat("my-bot")

    answer = client.send_message(
        chat_id,
        "Show me what you can do."
    )

    print(answer)
```

The consuming application does not need to know the underlying REST endpoints or response structure.