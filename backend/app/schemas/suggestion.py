from datetime import datetime
from pydantic import BaseModel


class SuggestionOut(BaseModel):
    id: int
    account_id: int
    sender_email: str
    sender_domain: str
    email_count: int
    suggested_label: str
    suggested_action: str
    criteria_json: str
    ai_rationale: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
