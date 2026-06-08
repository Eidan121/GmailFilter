from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.services.oauth import load_token


def get_service(encrypted_token: str | None):
    creds = load_token(encrypted_token)
    if not creds:
        raise PermissionError("Token invalid or expired — re-authenticate this account.")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)
