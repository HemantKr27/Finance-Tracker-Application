from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.schemas.account import AccountCreate, AccountResponse
from app.crud import account as account_crud
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=AccountResponse)
def create_account(
       account: AccountCreate,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user)
       ):
       return account_crud.create_account(db, account, current_user.id)

@router.get("/", response_model=list[AccountResponse])
def get_my_accounts(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
      return account_crud.get_accounts_by_user(db, current_user.id)