from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    Enum,
    DateTime,
    Boolean,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    func,
    text
)
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
from app.models.enums import BudgetPeriod, BudgetStatus


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)

    period = Column(Enum(BudgetPeriod), nullable=False)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    threshold_percentage = Column(Integer, nullable=False, default=80)

    status = Column(
        Enum(BudgetStatus),
        nullable=False,
        default=BudgetStatus.active
    )

    is_recurring = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship(
    "User",
    back_populates="budgets")
    budget_categories = relationship(
    "BudgetCategory",
    back_populates="budget",
    cascade="all, delete-orphan"
    )