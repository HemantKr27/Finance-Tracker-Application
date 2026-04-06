from pydantic import BaseModel, Field
from app.models.enums import TransactionType

class CategoryBase(BaseModel):
    name: str = Field(..., example="Food")
    type: TransactionType = Field(..., example="expense")

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    user_id: int | None  # nullable in model

    class Config:
        from_attributes = True