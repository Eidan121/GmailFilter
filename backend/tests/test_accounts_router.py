from datetime import datetime
from types import SimpleNamespace

import httpx
import pytest
from google.oauth2.credentials import Credentials

from app.models.account import GmailAccount
from app.services import oauth as oauth_svc


def _fake_creds(token="access-token-123"):
    return Credentials(
        token=token,
        refresh_token="refresh-token-456",
        token_uri="https://oauth2.googleapis.com/token",
        client_id="test-client-id.apps.googleusercontent.com",
        client_secret="test-client-secret",
        scopes=oauth_svc.SCOPES,
    )


def test_connect_returns_503_when_oauth_client_not_configured(client, monkeypatch):
    monkeypatch.setattr(oauth_svc.settings, "google_client_id", "")
    monkeypatch.setattr(oauth_svc.settings, "google_client_secret", "")

    resp = client.post("/api/accounts/connect")

    assert resp.status_code == 503
    assert "GOOGLE_CLIENT_ID" in resp.json()["detail"]


def test_connect_returns_auth_url_when_configured(client, google_oauth_settings):
    resp = client.post("/api/accounts/connect")

    assert resp.status_code == 200
    body = resp.json()
    assert body["auth_url"].startswith("https://accounts.google.com/o/oauth2/auth")
    assert body["state"]


def test_callback_creates_account_with_encrypted_token(client, db_session, monkeypatch, tmp_path, stub_token_refresh):
    monkeypatch.setattr(oauth_svc.settings, "data_dir", tmp_path)
    monkeypatch.setattr(oauth_svc.settings, "token_encryption_key", "")
    monkeypatch.setattr(oauth_svc, "exchange_code", lambda state, code: _fake_creds())
    monkeypatch.setattr(
        httpx,
        "get",
        lambda *a, **kw: SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"email": "user@gmail.com", "name": "Test User"},
        ),
    )

    resp = client.get("/api/accounts/callback", params={"code": "auth-code", "state": "some-state"})

    assert resp.status_code == 200
    account = db_session.query(GmailAccount).filter_by(email="user@gmail.com").one()
    assert account.display_name == "Test User"
    assert account.is_active is True
    assert account.encrypted_token is not None
    assert account.encrypted_token != _fake_creds().to_json()

    # The stored token decrypts back to working credentials
    loaded = oauth_svc.load_token(account.encrypted_token)
    assert loaded.token == "access-token-123"


def test_callback_rolls_over_token_on_reconnect(client, db_session, monkeypatch, tmp_path, stub_token_refresh):
    monkeypatch.setattr(oauth_svc.settings, "data_dir", tmp_path)
    monkeypatch.setattr(oauth_svc.settings, "token_encryption_key", "")
    monkeypatch.setattr(oauth_svc, "exchange_code", lambda state, code: _fake_creds(token="first-token"))
    monkeypatch.setattr(
        httpx,
        "get",
        lambda *a, **kw: SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"email": "user@gmail.com", "name": "Test User"},
        ),
    )
    client.get("/api/accounts/callback", params={"code": "code-1", "state": "state-1"})
    first = db_session.query(GmailAccount).filter_by(email="user@gmail.com").one()
    first_encrypted = first.encrypted_token

    monkeypatch.setattr(oauth_svc, "exchange_code", lambda state, code: _fake_creds(token="second-token"))
    client.get("/api/accounts/callback", params={"code": "code-2", "state": "state-2"})

    accounts = db_session.query(GmailAccount).filter_by(email="user@gmail.com").all()
    assert len(accounts) == 1  # upserted, not duplicated
    rolled = accounts[0]
    assert rolled.encrypted_token != first_encrypted
    assert oauth_svc.load_token(rolled.encrypted_token).token == "second-token"


def test_callback_rejects_unknown_state(client, monkeypatch):
    def _raise(state, code):
        raise ValueError(f"No pending OAuth flow for state={state}")

    monkeypatch.setattr(oauth_svc, "exchange_code", _raise)

    resp = client.get("/api/accounts/callback", params={"code": "auth-code", "state": "bogus"})

    assert resp.status_code == 400


def test_list_accounts_returns_connected_accounts(client, db_session):
    db_session.add(GmailAccount(email="a@gmail.com", encrypted_token="enc-a", is_active=True))
    db_session.add(GmailAccount(email="b@gmail.com", encrypted_token="enc-b", is_active=False))
    db_session.commit()

    resp = client.get("/api/accounts")

    assert resp.status_code == 200
    emails = {row["email"] for row in resp.json()}
    assert emails == {"a@gmail.com", "b@gmail.com"}


def test_delete_account_removes_row(client, db_session):
    account = GmailAccount(email="a@gmail.com", encrypted_token="enc-a", is_active=True)
    db_session.add(account)
    db_session.commit()
    account_id = account.id

    resp = client.delete(f"/api/accounts/{account_id}")

    assert resp.status_code == 204
    assert db_session.get(GmailAccount, account_id) is None


def test_delete_account_404_for_unknown_id(client):
    resp = client.delete("/api/accounts/999")

    assert resp.status_code == 404


def test_status_reports_active_when_token_loads(client, db_session, monkeypatch):
    account = GmailAccount(
        email="a@gmail.com",
        encrypted_token="enc-a",
        is_active=False,
        last_seen=datetime.utcnow(),
    )
    db_session.add(account)
    db_session.commit()

    monkeypatch.setattr(oauth_svc, "load_token", lambda enc: _fake_creds())

    resp = client.get(f"/api/accounts/{account.id}/status")

    assert resp.status_code == 200
    assert resp.json() == {"id": account.id, "email": "a@gmail.com", "is_active": True}
    db_session.refresh(account)
    assert account.is_active is True


def test_status_reports_inactive_when_token_invalid(client, db_session, monkeypatch):
    account = GmailAccount(email="a@gmail.com", encrypted_token="enc-a", is_active=True)
    db_session.add(account)
    db_session.commit()

    monkeypatch.setattr(oauth_svc, "load_token", lambda enc: None)

    resp = client.get(f"/api/accounts/{account.id}/status")

    assert resp.status_code == 200
    assert resp.json()["is_active"] is False
    db_session.refresh(account)
    assert account.is_active is False
