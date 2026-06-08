from datetime import datetime
from pydantic import BaseModel


class ScanStatus(BaseModel):
    last_run: datetime | None
    next_run: datetime | None
    pending_suggestions: int
    is_running: bool


class ScanResultOut(BaseModel):
    id: int
    account_id: int
    scanned_at: datetime
    emails_scanned: int
    flood_count: int
    duration_sec: float

    model_config = {"from_attributes": True}
