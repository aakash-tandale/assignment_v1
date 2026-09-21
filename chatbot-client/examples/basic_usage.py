from chatbot_client import ChatbotClient


def main():
    with ChatbotClient(
        base_url="http://127.0.0.1:8000",
        max_retries=2,
        retry_backoff_factor=0.5,
    ) as client:

        chat_id = client.create_chat("test-bot")

        print(f"Created chat: {chat_id}")

        answer = client.send_message(
            chat_id,
            "Hello, how are you?"
        )

        print(f"Assistant: {answer}")


if __name__ == "__main__":
    main()