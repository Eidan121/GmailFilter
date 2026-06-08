import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.account import GmailAccount
from app.models.suggestion import FilterSuggestion
from app.schemas.filter import FilterAction, FilterCriteria, FilterCreate
from app.schemas.label import LabelCreate
from app.services import filter_service, label_service


def apply_suggestion(db: Session, suggestion_id: int) -> FilterSuggestion:
    suggestion = db.get(FilterSuggestion, suggestion_id)
    if suggestion is None:
        raise ValueError(f"Suggestion {suggestion_id} not found")
    if suggestion.status != "pending":
        raise ValueError(f"Suggestion already {suggestion.status}")

    account = db.get(GmailAccount, suggestion.account_id)
    if not account or not account.is_active:
        raise PermissionError("Account not active — re-authenticate")

    labels = label_service.list_labels(account.encrypted_token)
    label_id = next(
        (lbl.id for lbl in labels if lbl.name.lower() == suggestion.suggested_label.lower()),
        None,
    )
    if not label_id:
        new_label = label_service.create_label(
            account.encrypted_token, LabelCreate(name=suggestion.suggested_label)
        )
        label_id = new_label.id

    criteria_dict = json.loads(suggestion.criteria_json)
    remove_ids = ["INBOX"] if "archive" in suggestion.suggested_action else []

    filter_service.create_filter(
        account.encrypted_token,
        suggestion.account_id,
        FilterCreate(
            criteria=FilterCriteria(from_=criteria_dict.get("from")),
            action=FilterAction(add_label_ids=[label_id], remove_label_ids=remove_ids),
        ),
        db,
    )

    suggestion.status = "accepted"
    suggestion.acted_at = datetime.utcnow()
    db.commit()
    db.refresh(suggestion)
    return suggestion


def dismiss_suggestion(db: Session, suggestion_id: int) -> FilterSuggestion:
    suggestion = db.get(FilterSuggestion, suggestion_id)
    if suggestion is None:
        raise ValueError(f"Suggestion {suggestion_id} not found")
    suggestion.status = "dismissed"
    suggestion.acted_at = datetime.utcnow()
    db.commit()
    db.refresh(suggestion)
    return suggestion
