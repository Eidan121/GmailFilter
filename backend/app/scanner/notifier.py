import asyncio
import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.scan_result import ScanResult
from app.models.suggestion import FilterSuggestion

# Single in-process SSE queue
_sse_queue: asyncio.Queue = asyncio.Queue()


def get_sse_queue() -> asyncio.Queue:
    return _sse_queue


def persist_scan(
    db: Session,
    account_id: int,
    emails_scanned: int,
    flood_count: int,
    duration_sec: float,
) -> ScanResult:
    result = ScanResult(
        account_id=account_id,
        emails_scanned=emails_scanned,
        flood_count=flood_count,
        duration_sec=duration_sec,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def upsert_suggestion(
    db: Session,
    account_id: int,
    scan_result_id: int,
    sender_email: str,
    sender_domain: str,
    email_count: int,
    suggested_label: str,
    suggested_action: str,
    criteria_json: str,
    ai_rationale: str | None,
) -> FilterSuggestion:
    existing = (
        db.query(FilterSuggestion)
        .filter_by(account_id=account_id, sender_email=sender_email, status="pending")
        .first()
    )
    if existing:
        existing.email_count = email_count
        existing.suggested_label = suggested_label
        existing.suggested_action = suggested_action
        existing.criteria_json = criteria_json
        existing.ai_rationale = ai_rationale
        db.commit()
        db.refresh(existing)
        return existing

    suggestion = FilterSuggestion(
        account_id=account_id,
        scan_result_id=scan_result_id,
        sender_email=sender_email,
        sender_domain=sender_domain,
        email_count=email_count,
        suggested_label=suggested_label,
        suggested_action=suggested_action,
        criteria_json=criteria_json,
        ai_rationale=ai_rationale,
        status="pending",
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion


def emit_event(event_type: str, payload: dict) -> None:
    """Non-blocking push to SSE queue (fire-and-forget from sync context)."""
    data = json.dumps({"type": event_type, "payload": payload})
    try:
        _sse_queue.put_nowait(data)
    except asyncio.QueueFull:
        pass
