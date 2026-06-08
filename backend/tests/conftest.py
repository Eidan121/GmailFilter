from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from google.oauth2.credentials import Credentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def stub_token_refresh(monkeypatch):
    """Credentials loaded from JSON come back with a near-past `expiry`, so
    `load_token` always tries to refresh them. Stub that out so tests don't
    hit Google's token endpoint — pretend the refresh succeeded and the
    access token is now valid for another hour."""

    def fake_refresh(self, request):
        self.token = self.token or "refreshed-token"
        self.expiry = datetime.utcnow() + timedelta(hours=1)

    monkeypatch.setattr(Credentials, "refresh", fake_refresh)


@pytest.fixture()
def google_oauth_settings(monkeypatch):
    """Configure a fake Google OAuth client so oauth_svc.get_auth_url() succeeds."""
    monkeypatch.setattr(settings, "google_client_id", "test-client-id.apps.googleusercontent.com")
    monkeypatch.setattr(settings, "google_client_secret", "test-client-secret")
    monkeypatch.setattr(settings, "token_encryption_key", "")
    return settings
