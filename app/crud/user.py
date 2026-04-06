from sqlalchemy.orm import Session
from app.models.user import User
from app.models.account import Account
from decimal import Decimal
from app.utils.security import hash_password
from app.crud.category import create_default_categories

def create_user(db: Session, username: str, email: str, password: str):
    hashed = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    default_account = Account(
        name="Cash",
        type="cash",
        balance=Decimal("0.00"),
        user_id=user.id
    )
    db.add(default_account)
    db.commit()
    db.refresh(default_account)

    create_default_categories(db,user.id)

    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username==username).first()