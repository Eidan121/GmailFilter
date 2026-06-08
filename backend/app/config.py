from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GmailFilter"

    data_dir: Path = Path.home() / ".gmail_filter_app"

    # Postgres connection string. The default targets the `db` service from
    # docker-compose; override via .env for local (non-Docker) development,
    # e.g. postgresql+psycopg://gmailfilter:gmailfilter@localhost:5432/gmailfilter
    database_url: str = "postgresql+psycopg://gmailfilter:gmailfilter@db:5432/gmailfilter"

    @property
    def token_key_path(self) -> Path:
        return self.data_dir / "token.key"

    google_client_id: str = ""
    google_client_secret: str = ""
    # Optional: fixed Fernet key for encrypting stored tokens. If unset, a key
    # is generated on first run and persisted to token_key_path.
    token_encryption_key: str = ""

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_origin: str = "http://localhost:5173"

    flood_threshold: int = 20
    scan_interval_hours: int = 6
    max_messages_per_scan: int = 2500

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
