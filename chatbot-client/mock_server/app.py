"""
Mock chatbot API used only for local development and testing.

This is NOT the real chatbot backend.
It implements only the two API operations required
by the assignment.
"""

from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="Mock Chatbot API",
)


class CreateChatRequest(BaseModel):
    botId: str


class ChatCompletionRequest(BaseModel):
    userMessage: str
    ignoreChatHistory: bool = False
    isAdminChat: bool = False
    isTraceLogEnabled: bool = False


@app.post("/api/chats")
def create_chat(request: CreateChatRequest):
    return {
        "chatId": str(uuid4()),
        "botId": request.botId,
    }


@app.post("/api/chats/{chat_id}/completions")
def chat_completion(
    chat_id: str,
    request: ChatCompletionRequest,
):
    return {
        "completionId": str(uuid4()),
        "chatId": chat_id,
        "userMessage": request.userMessage,
        "assistantMessage": (
            f"Mock response for: {request.userMessage}"
        ),
    }