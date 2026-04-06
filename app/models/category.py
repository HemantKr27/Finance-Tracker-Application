from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint, text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.enums import TransactionType


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)
    type = Column(Enum(TransactionType, name="transaction_type"), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("name", "user_id", name="unique_category_per_user"),
    )

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budget_categories = relationship("BudgetCategory",back_populates="category", cascade="all, delete-orphan")