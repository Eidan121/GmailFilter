from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.account import GmailAccount
from app.schemas.label import LabelCreate, LabelOut, LabelUpdate
from app.services import label_service

router = APIRouter()


def _get_account(account_id: int, db: Session) -> GmailAccount:
    account = db.get(GmailAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not account.is_active:
        raise HTTPException(status_code=403, detail="Account token expired — re-authenticate")
    return account


@router.get("", response_model=list[LabelOut])
def list_labels(account_id: int, db: Session = Depends(get_db)):
    account = _get_account(account_id, db)
    return label_service.list_labels(account.encrypted_token)


@router.post("", response_model=LabelOut, status_code=201)
def create_label(account_id: int, data: LabelCreate, db: Session = Depends(get_db)):
    account = _get_account(account_id, db)
    return label_service.create_label(account.encrypted_token, data)


@router.patch("/{label_id}", response_model=LabelOut)
def update_label(account_id: int, label_id: str, data: LabelUpdate, db: Session = Depends(get_db)):
    account = _get_account(account_id, db)
    return label_service.update_label(account.encrypted_token, label_id, data)


@router.delete("/{label_id}", status_code=204)
def delete_label(account_id: int, label_id: str, db: Session = Depends(get_db)):
    account = _get_account(account_id, db)
    label_service.delete_label(account.encrypted_token, label_id)
