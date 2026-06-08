import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.account import GmailAccount
from app.models.suggestion import FilterSuggestion
from app.schemas.filter import FilterCriteria, FilterAction, FilterCreate
from app.schemas.suggestion import SuggestionOut
from app.services import filter_service

router = APIRouter()


@router.get("", response_model=list[SuggestionOut])
def list_suggestions(
    account_id: int | None = Query(None),
    status: str = Query("pending"),
    db: Session = Depends(get_db),
):
    q = db.query(FilterSuggestion).filter_by(status=status)
    if account_id is not None:
        q = q.filter_by(account_id=account_id)
    return q.order_by(FilterSuggestion.email_count.desc()).all()


@router.post("/{suggestion_id}/accept", response_model=SuggestionOut)
def accept_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    suggestion = db.get(FilterSuggestion, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    if suggestion.status != "pending":
        raise HTTPException(status_code=400, detail=f"Suggestion already {suggestion.status}")

    account = db.get(GmailAccount, suggestion.account_id)
    if not account or not account.is_active:
        raise HTTPException(status_code=403, detail="Account not active")

    # Resolve or create the label
    from app.services.label_service import list_labels, create_label
    from app.schemas.label import LabelCreate

    labels = list_labels(account.encrypted_token)
    label_id = next((l.id for l in labels if l.name.lower() == suggestion.suggested_label.lower()), None)
    if not label_id:
        new_label = create_label(account.encrypted_token, LabelCreate(name=suggestion.suggested_label))
        label_id = new_label.id

    criteria_dict = json.loads(suggestion.criteria_json)
    add_label_ids = [label_id]
    remove_label_ids = ["INBOX"] if "archive" in suggestion.suggested_action else []

    filter_data = FilterCreate(
        criteria=FilterCriteria(from_=criteria_dict.get("from")),
        action=FilterAction(add_label_ids=add_label_ids, remove_label_ids=remove_label_ids),
    )
    filter_service.create_filter(account.encrypted_token, suggestion.account_id, filter_data, db)

    suggestion.status = "accepted"
    suggestion.acted_at = datetime.utcnow()
    db.commit()
    db.refresh(suggestion)
    return suggestion


@router.post("/{suggestion_id}/dismiss", response_model=SuggestionOut)
def dismiss_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    suggestion = db.get(FilterSuggestion, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    suggestion.status = "dismissed"
    suggestion.acted_at = datetime.utcnow()
    db.commit()
    db.refresh(suggestion)
    return suggestion


@router.delete("/{suggestion_id}", status_code=204)
def delete_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    suggestion = db.get(FilterSuggestion, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    db.delete(suggestion)
    db.commit()
