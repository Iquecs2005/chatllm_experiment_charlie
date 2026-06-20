from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from backend.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestUserModel:
    def test_create_user(self, db_session):
        """Deve criar um usuario com email e password_hash."""
        user = User(email="test@example.com", password_hash=pwd_context.hash("senha123"))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.password_hash != "senha123"  # Hash != plain text
        assert pwd_context.verify("senha123", user.password_hash)

    def test_email_unique_constraint(self, db_session):
        """Email deve ser unico."""
        user1 = User(email="duplicate@example.com", password_hash="hash1")
        user2 = User(email="duplicate@example.com", password_hash="hash2")
        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()


class TestAuthAPI:
    def test_register(self, client: TestClient):
        """Deve registrar um novo usuario e retornar token."""
        response = client.post(
            "/api/auth/register",
            json={"email": "new@example.com", "password": "senha123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self, client: TestClient):
        """Email duplicado deve retornar 409."""
        client.post("/api/auth/register", json={"email": "dup@example.com", "password": "senha123"})
        response = client.post("/api/auth/register", json={"email": "dup@example.com", "password": "outra123"})
        assert response.status_code == 409

    def test_login_success(self, client: TestClient):
        """Login com credenciais corretas deve retornar token."""
        client.post("/api/auth/register", json={"email": "login@example.com", "password": "senha123"})
        response = client.post("/api/auth/login", json={"email": "login@example.com", "password": "senha123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self, client: TestClient):
        """Login com senha errada deve retornar 401."""
        client.post("/api/auth/register", json={"email": "wrong@example.com", "password": "senha123"})
        response = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "senha_errada"})
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Login com email nao cadastrado deve retornar 401."""
        response = client.post("/api/auth/login", json={"email": "noone@example.com", "password": "senha123"})
        assert response.status_code == 401

    def test_get_me_authenticated(self, client: TestClient):
        """GET /me com token valido deve retornar dados do usuario."""
        reg_resp = client.post("/api/auth/register", json={"email": "me@example.com", "password": "senha123"})
        token = reg_resp.json()["access_token"]

        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"

    def test_get_me_unauthenticated(self, client: TestClient):
        """GET /me sem token deve retornar 401."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_logout(self, client: TestClient):
        """Logout deve retornar sucesso."""
        response = client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    def test_register_invalid_email(self, client: TestClient):
        """Email invalido deve retornar 422."""
        response = client.post(
            "/api/auth/register",
            json={"email": "invalido", "password": "senha123"},
        )
        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Senha muito curta deve retornar 422."""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "123"},
        )
        assert response.status_code == 422

    def test_session_ownership(self, client: TestClient):
        """Sessoes criadas apos login devem pertencer ao usuario."""
        reg_resp = client.post("/api/auth/register", json={"email": "owner@example.com", "password": "senha123"})
        token = reg_resp.json()["access_token"]

        # Create session with auth
        create_resp = client.post(
            "/api/sessions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create_resp.status_code == 201
        session_id = create_resp.json()["id"]

        # List sessions with auth — should see the session
        list_resp = client.get(
            "/api/sessions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_resp.status_code == 200
        assert len(list_resp.json()["sessions"]) == 1