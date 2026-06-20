from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.models import Session


class TestSessionModel:
    def test_create_session_defaults(self, db_session):
        """Deve criar uma sessao com valores padrao."""
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, title="Novo Chat")
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.id == session_id
        assert session.title == "Novo Chat"
        assert session.created_at is not None
        assert session.updated_at is not None

    def test_session_custom_title(self, db_session):
        """Deve criar uma sessao com titulo customizado."""
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, title="Meu Chat")
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.title == "Meu Chat"


class TestSessionAPI:
    def test_list_sessions_empty(self, client: TestClient):
        """Lista de sessoes deve ser vazia inicialmente."""
        response = client.get("/api/sessions")
        assert response.status_code == 200
        data = response.json()
        assert data["sessions"] == []

    def test_create_session(self, client: TestClient):
        """Deve criar uma nova sessao."""
        response = client.post("/api/sessions")
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Novo Chat"

    def test_list_sessions_after_create(self, client: TestClient):
        """Deve listar sessoes apos criar uma."""
        client.post("/api/sessions")
        response = client.get("/api/sessions")
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["title"] == "Novo Chat"

    def test_delete_session(self, client: TestClient):
        """Deve deletar uma sessao."""
        create_resp = client.post("/api/sessions")
        session_id = create_resp.json()["id"]

        delete_resp = client.delete(f"/api/sessions/{session_id}")
        assert delete_resp.status_code == 204

        # Verify it's gone
        list_resp = client.get("/api/sessions")
        assert len(list_resp.json()["sessions"]) == 0

    def test_delete_nonexistent_session(self, client: TestClient):
        """Deve retornar 404 ao deletar sessao inexistente."""
        response = client.delete("/api/sessions/nonexistent-id")
        assert response.status_code == 404

    def test_get_session_messages_empty(self, client: TestClient):
        """Sessao nova deve ter lista de mensagens vazia."""
        create_resp = client.post("/api/sessions")
        session_id = create_resp.json()["id"]

        response = client.get(f"/api/sessions/{session_id}/messages")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_session_messages_nonexistent(self, client: TestClient):
        """Deve retornar 404 ao buscar mensagens de sessao inexistente."""
        response = client.get("/api/sessions/nonexistent-id/messages")
        assert response.status_code == 404

    def test_generate_title(self, client: TestClient):
        """Deve gerar e atualizar titulo da sessao."""
        create_resp = client.post("/api/sessions")
        session_id = create_resp.json()["id"]

        response = client.post(
            "/api/sessions/generate-title",
            json={
                "session_id": session_id,
                "message": "Qual a capital do Brasil?",
                "reply": "A capital do Brasil e Brasilia.",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert "Brasil" in data["title"]

    def test_generate_title_nonexistent_session(self, client: TestClient):
        """Deve retornar 404 ao gerar titulo para sessao inexistente."""
        response = client.post(
            "/api/sessions/generate-title",
            json={
                "session_id": "nonexistent-id",
                "message": "Ola",
                "reply": "Oi",
            },
        )
        assert response.status_code == 404

    def test_chat_with_session_id(self, client: TestClient):
        """O endpoint /api/chat deve aceitar session_id e criar sessao automaticamente."""
        # Create a session first
        create_resp = client.post("/api/sessions")
        session_id = create_resp.json()["id"]

        # Chat with that session_id
        response = client.post(
            "/api/chat",
            json={"message": "Ola", "session_id": session_id},
        )
        # Can fail with 503 (no API key) but should not be 422
        assert response.status_code in (200, 503)

        if response.status_code == 503:
            # Even with error, the session should still exist
            msg_resp = client.get(f"/api/sessions/{session_id}/messages")
            # Messages might be empty since chat failed
            assert msg_resp.status_code == 200

    def test_auto_title_generated_via_generate_title(self, client: TestClient):
        """O titulo deve ser gerado automaticamente a partir da primeira mensagem e resposta."""
        create_resp = client.post("/api/sessions")
        session_id = create_resp.json()["id"]

        # Gerar titulo baseado na primeira interacao
        resp = client.post(
            "/api/sessions/generate-title",
            json={
                "session_id": session_id,
                "message": "Explique o que é Python",
                "reply": "Python é uma linguagem de programação de alto nível.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == session_id
        # O titulo deve ser extraido do inicio da mensagem do usuario
        assert "Explique" in data["title"]
        # O titulo nao deve ser mais "Novo Chat"
        assert data["title"] != "Novo Chat"

    def test_auto_title_truncated_to_50_chars(self, client: TestClient):
        """O titulo gerado deve ser truncado em ~50 caracteres."""
        create_resp = client.post("/api/sessions")
        session_id = create_resp.json()["id"]

        long_message = "Esta é uma mensagem muito longa que deve ser truncada pois ultrapassa o limite de caracteres definido para o titulo da sessao"
        resp = client.post(
            "/api/sessions/generate-title",
            json={
                "session_id": session_id,
                "message": long_message,
                "reply": "Resposta curta.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # Titulo deve conter o inicio da mensagem truncado
        assert data["title"].startswith("Esta")
        assert len(data["title"]) <= 55  # ~50 chars + possivel variacao

    def test_auto_title_takes_first_line_only(self, client: TestClient):
        """O titulo deve usar apenas a primeira linha da mensagem."""
        create_resp = client.post("/api/sessions")
        session_id = create_resp.json()["id"]

        resp = client.post(
            "/api/sessions/generate-title",
            json={
                "session_id": session_id,
                "message": "Python\né uma linguagem de programação.",
                "reply": "Sim, Python é versátil.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Python"

    def test_auto_title_persisted_in_db(self, db_session, client: TestClient):
        """O titulo gerado deve ser persistido no banco."""
        from backend.models import Session

        create_resp = client.post("/api/sessions")
        session_id = create_resp.json()["id"]

        client.post(
            "/api/sessions/generate-title",
            json={
                "session_id": session_id,
                "message": "Qual a capital da Franca?",
                "reply": "Paris.",
            },
        )

        session = db_session.query(Session).filter(Session.id == session_id).first()
        assert session is not None
        assert "capital" in session.title or "Franca" in session.title
        assert session.title != "Novo Chat"

    def test_title_is_fixed_after_first_generation(self, client: TestClient):
        """O titulo nao deve mudar apos ser gerado pela primeira vez."""
        create_resp = client.post("/api/sessions")
        session_id = create_resp.json()["id"]

        # Primeira geracao
        resp1 = client.post(
            "/api/sessions/generate-title",
            json={
                "session_id": session_id,
                "message": "Qual a capital do Brasil?",
                "reply": "Brasilia.",
            },
        )
        assert resp1.status_code == 200
        first_title = resp1.json()["title"]
        assert "capital" in first_title or "Brasil" in first_title

        # Segunda geracao com contexto diferente — deve manter o titulo original
        resp2 = client.post(
            "/api/sessions/generate-title",
            json={
                "session_id": session_id,
                "message": "Explique sobre Python",
                "reply": "Python e uma linguagem.",
            },
        )
        assert resp2.status_code == 200
        assert resp2.json()["title"] == first_title