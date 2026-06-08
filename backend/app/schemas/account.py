from datetime import datetime
from pydantic import BaseModel


class AccountOut(BaseModel):
    id: int
    email: str
    display_name: str | None
    is_active: bool
    last_seen: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class OAuthStartResponse(BaseModel):
    auth_url: str
    state: str


class AccountStatus(BaseModel):
    id: int
    email: str
    is_active: bool
