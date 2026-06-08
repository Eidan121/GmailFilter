import pytest

from app.models.account import GmailAccount


def test_account_persists_encrypted_token(db_session):
    account = GmailAccount(email="user@gmail.com", encrypted_token="cipher-text", is_active=True)
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)

    fetched = db_session.get(GmailAccount, account.id)
    assert fetched.encrypted_token == "cipher-text"
    assert fetched.email == "user@gmail.com"


def test_account_allows_null_token_before_first_connect(db_session):
    account = GmailAccount(email="pending@gmail.com", is_active=False)
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)

    assert db_session.get(GmailAccount, account.id).encrypted_token is None


def test_account_email_is_unique(db_session):
    db_session.add(GmailAccount(email="dup@gmail.com", encrypted_token="a"))
    db_session.commit()

    db_session.add(GmailAccount(email="dup@gmail.com", encrypted_token="b"))
    with pytest.raises(Exception):
        db_session.commit()
