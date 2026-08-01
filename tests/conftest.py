from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.database import Base
from app.main import app


TEST_DATABASE_URL = "sqlite://"


engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def preparar_banco():
    Base.metadata.create_all(bind=engine_test)

    yield

    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def usuario_criado(client):
    payload = {
        "nome": "Usuário Teste",
        "email": "teste@example.com",
        "senha": "senha123",
    }

    response = client.post(
        "/usuarios",
        json=payload,
    )

    assert response.status_code == 201

    return payload


@pytest.fixture
def token(client, usuario_criado):
    response = client.post(
        "/auth/login",
        data={
            "username": usuario_criado["email"],
            "password": usuario_criado["senha"],
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
    }
