from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.account import GmailAccount
from app.schemas.filter import FilterCreate, FilterOut
from app.services import filter_service

router = APIRouter()


def _get_account(account_id: int, db: Session) -> GmailAccount:
    account = db.get(GmailAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not account.is_active:
        raise HTTPException(status_code=403, detail="Account token expired — re-authenticate")
    return account


@router.get("", response_model=list[FilterOut])
def list_filters(account_id: int, db: Session = Depends(get_db)):
    account = _get_account(account_id, db)
    return filter_service.list_filters(account.encrypted_token, account_id, db)


@router.post("", response_model=FilterOut, status_code=201)
def create_filter(account_id: int, data: FilterCreate, db: Session = Depends(get_db)):
    account = _get_account(account_id, db)
    return filter_service.create_filter(account.encrypted_token, account_id, data, db)


@router.delete("/{filter_id}", status_code=204)
def delete_filter(account_id: int, filter_id: str, db: Session = Depends(get_db)):
    account = _get_account(account_id, db)
    filter_service.delete_filter(account.encrypted_token, account_id, filter_id, db)
