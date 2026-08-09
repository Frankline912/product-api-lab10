import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from main import app, get_session, Base


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture
def session():
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(session):
    def get_test_session():
        yield session

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    }