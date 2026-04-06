from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.crud import transaction as transaction_crud
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):

    db_transaction = transaction_crud.create_transaction(
        db,
        transaction,
        current_user.id
        )
    
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Account or category not found")

    return db_transaction


@router.get("/", response_model=list[TransactionResponse])
def get_my_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    return transaction_crud.get_transactions_by_user(db, current_user.id)


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted_transaction = transaction_crud.delete_transaction(
        db,
        transaction_id,
        current_user.id
    )

    if not deleted_transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return {"message": "Transaction deleted successfully"}

