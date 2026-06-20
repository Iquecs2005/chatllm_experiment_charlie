from __future__ import annotations

import uuid
from datetime import datetime, timezone

from backend.models import ChatMessage, Session


class TestChatMessage:
    def test_create_message_defaults(self, db_session):
        """Deve criar uma mensagem com valores padrao para session_key, model e created_at."""
        msg = ChatMessage(
            role="user",
            content="Ola, mundo!",
        )
        db_session.add(msg)
        db_session.commit()
        db_session.refresh(msg)

        assert msg.id is not None
        assert msg.session_key == "default"
        assert msg.role == "user"
        assert msg.content == "Ola, mundo!"
        assert msg.model == "google/gemma-4-31b-it"
        assert isinstance(msg.created_at, datetime)

    def test_create_message_custom_session(self, db_session):
        """Deve criar uma mensagem com session_key customizada."""
        msg = ChatMessage(
            session_key="session-abc",
            role="assistant",
            content="Resposta do assistente.",
        )
        db_session.add(msg)
        db_session.commit()
        db_session.refresh(msg)

        assert msg.session_key == "session-abc"
        assert msg.role == "assistant"

    def test_create_message_custom_model(self, db_session):
        """Deve criar uma mensagem com modelo customizado."""
        msg = ChatMessage(
            role="user",
            content="Teste",
            model="openai/gpt-4o",
        )
        db_session.add(msg)
        db_session.commit()
        db_session.refresh(msg)

        assert msg.model == "openai/gpt-4o"

    def test_query_by_session_key(self, db_session):
        """Deve filtrar mensagens por session_key."""
        msg1 = ChatMessage(session_key="s1", role="user", content="a")
        msg2 = ChatMessage(session_key="s2", role="user", content="b")
        db_session.add_all([msg1, msg2])
        db_session.commit()

        results = (
            db_session.query(ChatMessage)
            .filter(ChatMessage.session_key == "s1")
            .all()
        )
        assert len(results) == 1
        assert results[0].content == "a"

    def test_query_by_role(self, db_session):
        """Deve filtrar mensagens pelo campo role."""
        msg1 = ChatMessage(role="user", content="pergunta")
        msg2 = ChatMessage(role="assistant", content="resposta")
        db_session.add_all([msg1, msg2])
        db_session.commit()

        users = (
            db_session.query(ChatMessage)
            .filter(ChatMessage.role == "user")
            .all()
        )
        assistants = (
            db_session.query(ChatMessage)
            .filter(ChatMessage.role == "assistant")
            .all()
        )

        assert len(users) == 1
        assert len(assistants) == 1
        assert users[0].content == "pergunta"
        assert assistants[0].content == "resposta"

    def test_created_at_auto_set(self, db_session):
        """O campo created_at deve ser preenchido automaticamente com UTC now."""
        before = datetime.now(timezone.utc).replace(tzinfo=None)
        msg = ChatMessage(role="user", content="timestamp test")
        db_session.add(msg)
        db_session.commit()
        db_session.refresh(msg)
        after = datetime.now(timezone.utc).replace(tzinfo=None)

        assert before <= msg.created_at <= after


class TestSession:
    def test_create_session_defaults(self, db_session):
        """Deve criar uma sessao com valores padrao."""
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, title="Novo Chat")
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.id == session_id
        assert session.title == "Novo Chat"
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.updated_at, datetime)

    def test_create_session_custom_title(self, db_session):
        """Deve criar uma sessao com titulo customizado."""
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, title="Meu Chat")
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.title == "Meu Chat"

    def test_session_created_at_auto_set(self, db_session):
        """O campo created_at deve ser preenchido automaticamente."""
        before = datetime.now(timezone.utc).replace(tzinfo=None)
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, title="Teste")
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        after = datetime.now(timezone.utc).replace(tzinfo=None)

        assert before <= session.created_at <= after

    def test_query_session_by_id(self, db_session):
        """Deve consultar sessao por ID."""
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, title="Unica")
        db_session.add(session)
        db_session.commit()

        result = db_session.query(Session).filter(Session.id == session_id).first()
        assert result is not None
        assert result.title == "Unica"

    def test_content_persists_long_text(self, db_session):
        """Deve persistir conteudos longos corretamente."""
        long_text = "Lorem ipsum " * 200
        msg = ChatMessage(role="user", content=long_text)
        db_session.add(msg)
        db_session.commit()
        db_session.refresh(msg)

        assert msg.content == long_text
