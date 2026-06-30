"""Shared pytest fixtures: an isolated in-memory SQLite DB per test, and a TestClient
with the `get_db` dependency overridden to use it."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (must import before `app.main` below so Base.metadata is fully populated)
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def citizen_token(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": "citizen@example.com",
            "password": "StrongPass123",
            "role": "citizen",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.fixture()
def admin_token(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Admin",
            "email": "admin@example.com",
            "password": "StrongPass123",
            "role": "municipality_admin",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(citizen_token):
    return {"Authorization": f"Bearer {citizen_token}"}


@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
