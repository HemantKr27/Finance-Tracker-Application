from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, text
from sqlalchemy.orm import relationship

from app.db.base import Base


class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id = Column(Integer, primary_key=True)

    budget_id = Column(
        Integer,
        ForeignKey("budgets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    allocated_amount = Column(Numeric(12, 2), nullable=False)
    alert_percentage = Column(Integer, nullable=False, default=80)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP")
    )

    budget = relationship(
        "Budget",
        back_populates="budget_categories"
    )

    category = relationship(
        "Category",
        back_populates="budget_categories"
    )