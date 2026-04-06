from sqlalchemy.orm import Session
from app.models.account import Account
from app.schemas.account import AccountCreate

def create_account(db: Session, account: AccountCreate, user_id: int):
    db_account = Account(
        name=account.name,
        type=account.type,
        balance=account.balance,
        user_id=user_id
    )

    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def get_accounts_by_user(db: Session, user_id: int):
    return db.query(Account).filter(Account.user_id == user_id).all()