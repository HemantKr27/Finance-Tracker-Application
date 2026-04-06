from sqlalchemy.orm import Session
from crud.user import get_user_by_email
from core.security import verify_password
from app.core.jwt import create_access_token

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    if not user:
        return None
    token_data = {"sub": str(user.id)}
    token = create_access_token(token_data)
    return token