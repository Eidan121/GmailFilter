from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.account import GmailAccount
from app.schemas.account import AccountOut, OAuthStartResponse
from app.services import oauth as oauth_svc

router = APIRouter()


@router.get("", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(GmailAccount).order_by(GmailAccount.created_at).all()


@router.post("/connect", response_model=OAuthStartResponse)
def connect_account():
    try:
        auth_url, state = oauth_svc.get_auth_url()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return OAuthStartResponse(auth_url=auth_url, state=state)


@router.get("/callback", response_class=HTMLResponse)
def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    try:
        creds = oauth_svc.exchange_code(state, code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Fetch email address from Google userinfo
    token = creds.token
    try:
        resp = httpx.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        userinfo = resp.json()
        email = userinfo.get("email", "unknown@gmail.com")
        display_name = userinfo.get("name")
    except Exception:
        email = "unknown@gmail.com"
        display_name = None

    # Upsert account row — each connect rolls over (replaces) any previously stored token
    account = db.query(GmailAccount).filter_by(email=email).first()
    if not account:
        account = GmailAccount(email=email, display_name=display_name, is_active=True)
        db.add(account)
        db.flush()  # get the generated id

    account.encrypted_token = oauth_svc.encrypt_token(creds)
    account.is_active = True
    account.last_seen = datetime.utcnow()
    if display_name:
        account.display_name = display_name
    db.commit()

    # Close the popup and signal the opener
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head><title>Connected</title></head>
<body>
<script>
  if (window.opener) {
    window.opener.postMessage({ type: 'oauth_complete' }, 'http://localhost:5173');
    window.close();
  } else {
    document.write('<p>Account connected. You may close this tab.</p>');
  }
</script>
</body>
</html>
""")


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.get(GmailAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()


@router.get("/{account_id}/status")
def account_status(account_id: int, db: Session = Depends(get_db)):
    account = db.get(GmailAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    creds = oauth_svc.load_token(account.encrypted_token)
    is_active = creds is not None
    if account.is_active != is_active:
        account.is_active = is_active
        db.commit()
    return {"id": account_id, "email": account.email, "is_active": is_active}
