import json

from sqlalchemy.orm import Session

from app.models.filter_cache import CachedFilter
from app.schemas.filter import FilterCreate, FilterOut
from app.services.gmail_client import get_service


def list_filters(encrypted_token: str | None, account_id: int, db: Session) -> list[FilterOut]:
    svc = get_service(encrypted_token)
    result = svc.users().settings().filters().list(userId="me").execute()
    raw_filters = result.get("filter", [])

    # Sync to cache
    db.query(CachedFilter).filter_by(account_id=account_id).delete()
    for f in raw_filters:
        db.add(CachedFilter(
            account_id=account_id,
            gmail_filter_id=f["id"],
            criteria_json=json.dumps(f.get("criteria", {})),
            action_json=json.dumps(f.get("action", {})),
        ))
    db.commit()

    return [FilterOut(id=f["id"], criteria=f.get("criteria", {}), action=f.get("action", {})) for f in raw_filters]


def create_filter(encrypted_token: str | None, account_id: int, data: FilterCreate, db: Session) -> FilterOut:
    svc = get_service(encrypted_token)
    body = {
        "criteria": _criteria_to_api(data.criteria),
        "action": _action_to_api(data.action),
    }
    created = svc.users().settings().filters().create(userId="me", body=body).execute()
    db.add(CachedFilter(
        account_id=account_id,
        gmail_filter_id=created["id"],
        criteria_json=json.dumps(created.get("criteria", {})),
        action_json=json.dumps(created.get("action", {})),
    ))
    db.commit()
    return FilterOut(id=created["id"], criteria=created.get("criteria", {}), action=created.get("action", {}))


def delete_filter(encrypted_token: str | None, account_id: int, filter_id: str, db: Session) -> None:
    svc = get_service(encrypted_token)
    svc.users().settings().filters().delete(userId="me", id=filter_id).execute()
    db.query(CachedFilter).filter_by(account_id=account_id, gmail_filter_id=filter_id).delete()
    db.commit()


def get_cached_filter_criteria(account_id: int, db: Session) -> set[str]:
    """Return all 'from' addresses already covered by a cached filter."""
    rows = db.query(CachedFilter).filter_by(account_id=account_id).all()
    addresses: set[str] = set()
    for row in rows:
        criteria = json.loads(row.criteria_json)
        if "from" in criteria:
            addresses.add(criteria["from"].lower())
    return addresses


def _criteria_to_api(c) -> dict:
    out: dict = {}
    if c.from_:
        out["from"] = c.from_
    if c.to:
        out["to"] = c.to
    if c.subject:
        out["subject"] = c.subject
    if c.query:
        out["query"] = c.query
    if c.has_attachment is not None:
        out["hasAttachment"] = c.has_attachment
    if c.exclude_chats is not None:
        out["excludeChats"] = c.exclude_chats
    return out


def _action_to_api(a) -> dict:
    out: dict = {}
    if a.add_label_ids:
        out["addLabelIds"] = a.add_label_ids
    if a.remove_label_ids:
        out["removeLabelIds"] = a.remove_label_ids
    if a.forward:
        out["forward"] = a.forward
    return out
