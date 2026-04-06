from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class AccountBase(BaseModel):
    name: str
    type: str
    balance: Decimal


class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
