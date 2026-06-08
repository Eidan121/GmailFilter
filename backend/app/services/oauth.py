import json
import uuid

from cryptography.fernet import Fernet
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.settings.basic",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

REDIRECT_URI = "http://localhost:8000/api/accounts/callback"

# In-memory store for pending OAuth states (state → flow serialization)
_pending_flows: dict[str, dict] = {}


def _client_config() -> dict:
    if not settings.google_client_id or not settings.google_client_secret:
        raise RuntimeError(
            "GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET are not configured. "
            "Set them in the backend .env (one-time operator setup in Google Cloud Console)."
        )
    return {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }


def _fernet() -> Fernet:
    """Load (or generate on first run) the symmetric key used to encrypt stored tokens."""
    if settings.token_encryption_key:
        return Fernet(settings.token_encryption_key.encode())

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    key_path = settings.token_key_path
    if not key_path.exists():
        key_path.write_bytes(Fernet.generate_key())
    return Fernet(key_path.read_bytes())


def get_auth_url() -> tuple[str, str]:
    """Start OAuth2 flow, return (auth_url, state)."""
    client_config = _client_config()
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    state = str(uuid.uuid4())
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )
    # Serialize flow so it can be reconstructed in the callback
    _pending_flows[state] = {
        "client_config": client_config,
        "scopes": SCOPES,
    }
    return auth_url, state


def exchange_code(state: str, code: str) -> Credentials:
    """Exchange authorization code for credentials."""
    flow_data = _pending_flows.pop(state, None)
    if not flow_data:
        raise ValueError(f"No pending OAuth flow for state={state}")
    flow = Flow.from_client_config(
        flow_data["client_config"],
        scopes=flow_data["scopes"],
        redirect_uri=REDIRECT_URI,
    )
    flow.fetch_token(code=code)
    return flow.credentials


def encrypt_token(creds: Credentials) -> str:
    """Serialize and encrypt credentials for storage in the database."""
    return _fernet().encrypt(creds.to_json().encode()).decode()


def load_token(encrypted_token: str | None) -> Credentials | None:
    """Decrypt stored credentials, refreshing them if expired."""
    if not encrypted_token:
        return None
    try:
        raw = _fernet().decrypt(encrypted_token.encode())
    except Exception:
        return None
    creds = Credentials.from_authorized_user_info(json.loads(raw), SCOPES)
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            return None
    return creds if creds.valid else None
