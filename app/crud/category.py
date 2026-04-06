from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.enums import TransactionType
from typing import List


def create_default_categories(db: Session, user_id: int) -> List[Category]:
    """
    Creates default categories for a new user with proper type.
    Returns the list of created Category objects.
    """
    default_categories = [
        {"name": "Food", "type": TransactionType.expense},
        {"name": "Transport", "type": TransactionType.expense},
        {"name": "Entertainment", "type": TransactionType.expense},
        {"name": "Salary", "type": TransactionType.income},
        {"name": "Other", "type": TransactionType.expense}
    ]

    categories = []

    for cat in default_categories:
        category = Category(
            name=cat["name"],
            type=cat["type"],
            user_id=user_id
        )
        db.add(category)
        categories.append(category)

    db.commit()

    # Refresh to get IDs and any defaults
    for category in categories:
        db.refresh(category)

    return categories




def create_category(db: Session, user_id: int, name: str, type: TransactionType):
    """
    Create a new category for a given user.
    Ensures the category name is unique per user.
    """
    # Check for existing category with same name for this user
    existing = db.query(Category).filter(
        Category.user_id == user_id,
        Category.name == name
    ).first()

    if existing:
        raise ValueError("Category with this name already exists")

    category = Category(
        name=name,
        type=type,
        user_id=user_id
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category

def get_user_categories(db: Session, user_id: int) -> List[Category]:
    """
    Fetch all categories for a given user.
    """
    return db.query(Category).filter(Category.user_id == user_id).all()
