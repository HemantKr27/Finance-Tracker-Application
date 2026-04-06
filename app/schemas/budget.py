from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BudgetCategoryBase(BaseModel):
    category_id: int
    allocated_amount: Decimal = Field(..., gt=0)
    alert_percentage: int = Field(default=80, ge=1, le=100)


class BudgetCategoryCreate(BudgetCategoryBase):
    pass


class BudgetCategoryUpdate(BaseModel):
    allocated_amount: Optional[Decimal] = Field(None, gt=0)
    alert_percentage: Optional[int] = Field(None, ge=1, le=100)


class BudgetCategoryResponse(BudgetCategoryBase):
    id: int
    spent_amount: Decimal = Decimal("0.00")
    remaining_amount: Decimal = Decimal("0.00")
    usage_percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class BudgetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    period: str = Field(default="monthly")

    start_date: date
    end_date: date

    threshold_percentage: int = Field(default=80, ge=1, le=100)
    is_recurring: bool = False
    status: str = Field(default="active")

    @field_validator("period")
    @classmethod
    def validate_period(cls, value):
        allowed = {"weekly", "monthly", "yearly"}
        if value not in allowed:
            raise ValueError(f"period must be one of {allowed}")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        allowed = {"active", "completed", "cancelled", "exceeded"}
        if value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        return self


class BudgetCreate(BudgetBase):
    categories: List[BudgetCategoryCreate]

    @model_validator(mode="after")
    def validate_categories(self):
        if not self.categories:
            raise ValueError("At least one category allocation is required")
        return self


class BudgetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    period: Optional[str] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    threshold_percentage: Optional[int] = Field(None, ge=1, le=100)
    is_recurring: Optional[bool] = None
    status: Optional[str] = None

    @field_validator("period")
    @classmethod
    def validate_period(cls, value):
        if value is None:
            return value

        allowed = {"weekly", "monthly", "yearly"}
        if value not in allowed:
            raise ValueError(f"period must be one of {allowed}")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value is None:
            return value

        allowed = {"active", "completed", "cancelled", "exceeded"}
        if value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date must be greater than or equal to start_date")
        return self


class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    amount: Decimal

    spent_amount: Decimal = Decimal("0.00")
    remaining_amount: Decimal = Decimal("0.00")
    usage_percentage: float = 0.0

    created_at: datetime
    updated_at: Optional[datetime] = None

    categories: List[BudgetCategoryResponse] = Field(
        default_factory=list,
        validation_alias="budget_categories",
    )

    model_config = ConfigDict(from_attributes=True)
