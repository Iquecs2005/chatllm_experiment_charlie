from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.schemas.chat import (
    ChatMessageIn,
    ChatRequest,
    ChatResponse,
    SessionCreateOut,
    SessionGenerateTitleRequest,
    SessionListOut,
    SessionOut,
)


class TestChatMessageIn:
    def test_valid_user_message(self):
        msg = ChatMessageIn(role="user", content="Ola!")
        assert msg.role == "user"
        assert msg.content == "Ola!"

    def test_valid_assistant_message(self):
        msg = ChatMessageIn(role="assistant", content="Resposta.")
        assert msg.role == "assistant"
        assert msg.content == "Resposta."

    def test_invalid_role(self):
        with pytest.raises(ValidationError):
            ChatMessageIn(role="system", content="Nao permitido")

    def test_empty_content(self):
        with pytest.raises(ValidationError):
            ChatMessageIn(role="user", content="")

    def test_content_too_long(self):
        with pytest.raises(ValidationError):
            ChatMessageIn(role="user", content="x" * 8001)


class TestChatRequest:
    def test_valid_request_minimal(self):
        req = ChatRequest(message="Hello")
        assert req.message == "Hello"
        assert req.model is None
        assert req.history == []
        assert req.session_id == "default"

    def test_valid_request_with_model(self):
        req = ChatRequest(message="Hi", model="openai/gpt-4o")
        assert req.model == "openai/gpt-4o"

    def test_valid_request_with_session_id(self):
        req = ChatRequest(message="Ola", session_id="abc-123")
        assert req.session_id == "abc-123"

    def test_valid_request_with_history(self):
        history = [
            ChatMessageIn(role="user", content="pergunta"),
            ChatMessageIn(role="assistant", content="resposta"),
        ]
        req = ChatRequest(message="continuacao", history=history)
        assert len(req.history) == 2
        assert req.history[0].role == "user"

    def test_empty_message(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_message_too_long(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="x" * 8001)

    def test_history_defaults_to_empty(self):
        req = ChatRequest(message="Hello")
        assert req.history == []


class TestChatResponse:
    def test_valid_response(self):
        resp = ChatResponse(reply="Resposta do modelo.", model="google/gemma-4-31b-it")
        assert resp.reply == "Resposta do modelo."
        assert resp.model == "google/gemma-4-31b-it"


class TestSessionOut:
    def test_valid_session_out(self):
        from datetime import datetime
        session = SessionOut(
            id="abc-123",
            title="Meu Chat",
            created_at=datetime(2025, 1, 1),
            updated_at=datetime(2025, 1, 1),
        )
        assert session.id == "abc-123"
        assert session.title == "Meu Chat"


class TestSessionListOut:
    def test_valid_session_list_out(self):
        from datetime import datetime
        data = SessionListOut(
            sessions=[
                SessionOut(
                    id="1",
                    title="Chat 1",
                    created_at=datetime(2025, 1, 1),
                    updated_at=datetime(2025, 1, 1),
                )
            ]
        )
        assert len(data.sessions) == 1


class TestSessionCreateOut:
    def test_valid_session_create_out(self):
        data = SessionCreateOut(id="abc", title="Novo Chat")
        assert data.id == "abc"
        assert data.title == "Novo Chat"


class TestSessionGenerateTitleRequest:
    def test_valid_request(self):
        req = SessionGenerateTitleRequest(
            session_id="abc-123",
            message="Qual a capital?",
            reply="Brasilia",
        )
        assert req.session_id == "abc-123"
        assert req.message == "Qual a capital?"

    def test_empty_message(self):
        with pytest.raises(ValidationError):
            SessionGenerateTitleRequest(
                session_id="abc",
                message="",
                reply="Brasilia",
            )

    def test_empty_reply(self):
        with pytest.raises(ValidationError):
            SessionGenerateTitleRequest(
                session_id="abc",
                message="Oi",
                reply="",
            )
