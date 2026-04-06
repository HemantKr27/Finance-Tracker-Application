from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from app.models.enums import TransactionType

class TransactionCreate(BaseModel):
    amount: Decimal
    description: str | None = None
    account_id: int
    category_id: int

class TransactionBase(TransactionCreate):
    type: TransactionType

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    transaction_date: datetime

    class Config:
        from_attributes = True
