import pytest
from google.oauth2.credentials import Credentials

from app.services import oauth as oauth_svc


def _fake_creds(token="access-token-123", refresh_token="refresh-token-456"):
    return Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id="test-client-id.apps.googleusercontent.com",
        client_secret="test-client-secret",
        scopes=oauth_svc.SCOPES,
    )


def test_client_config_requires_google_credentials(monkeypatch):
    monkeypatch.setattr(oauth_svc.settings, "google_client_id", "")
    monkeypatch.setattr(oauth_svc.settings, "google_client_secret", "")

    with pytest.raises(RuntimeError, match="GOOGLE_CLIENT_ID"):
        oauth_svc._client_config()


def test_get_auth_url_builds_url_and_tracks_pending_state(google_oauth_settings):
    oauth_svc._pending_flows.clear()

    auth_url, state = oauth_svc.get_auth_url()

    assert auth_url.startswith("https://accounts.google.com/o/oauth2/auth")
    assert f"state={state}" in auth_url
    assert state in oauth_svc._pending_flows
    assert oauth_svc._pending_flows[state]["scopes"] == oauth_svc.SCOPES


def test_exchange_code_raises_for_unknown_state(google_oauth_settings):
    oauth_svc._pending_flows.clear()

    with pytest.raises(ValueError, match="No pending OAuth flow"):
        oauth_svc.exchange_code("does-not-exist", "some-code")


def test_encrypt_and_load_token_round_trip(tmp_path, monkeypatch, stub_token_refresh):
    monkeypatch.setattr(oauth_svc.settings, "data_dir", tmp_path)
    monkeypatch.setattr(oauth_svc.settings, "token_encryption_key", "")

    creds = _fake_creds()
    encrypted = oauth_svc.encrypt_token(creds)

    assert encrypted != creds.to_json()  # actually stored encrypted, not plaintext

    loaded = oauth_svc.load_token(encrypted)

    assert loaded is not None
    assert loaded.token == creds.token
    assert loaded.refresh_token == creds.refresh_token


def test_load_token_returns_none_for_missing_or_invalid(tmp_path, monkeypatch):
    monkeypatch.setattr(oauth_svc.settings, "data_dir", tmp_path)
    monkeypatch.setattr(oauth_svc.settings, "token_encryption_key", "")

    assert oauth_svc.load_token(None) is None
    assert oauth_svc.load_token("") is None
    assert oauth_svc.load_token("not-a-valid-encrypted-blob") is None


def test_fernet_key_is_generated_once_and_reused(tmp_path, monkeypatch):
    monkeypatch.setattr(oauth_svc.settings, "data_dir", tmp_path)
    monkeypatch.setattr(oauth_svc.settings, "token_encryption_key", "")

    key_path = tmp_path / "token.key"
    assert not key_path.exists()

    first = oauth_svc._fernet()
    assert key_path.exists()
    persisted_key = key_path.read_bytes()

    second = oauth_svc._fernet()
    assert key_path.read_bytes() == persisted_key

    # Tokens encrypted with the first instance must decrypt with the second
    token = first.encrypt(b"hello")
    assert second.decrypt(token) == b"hello"


def test_fernet_uses_fixed_key_from_settings_when_provided(tmp_path, monkeypatch):
    from cryptography.fernet import Fernet

    fixed_key = Fernet.generate_key().decode()
    monkeypatch.setattr(oauth_svc.settings, "data_dir", tmp_path)
    monkeypatch.setattr(oauth_svc.settings, "token_encryption_key", fixed_key)

    f = oauth_svc._fernet()

    assert not (tmp_path / "token.key").exists()
    assert f.decrypt(Fernet(fixed_key.encode()).encrypt(b"x")) == b"x"
