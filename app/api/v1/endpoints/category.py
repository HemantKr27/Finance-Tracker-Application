from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.category import CategoryCreate, CategoryResponse
from app.models.user import User
from app.models.category import Category
from app.db.dependencies import get_db
from app.api.deps import get_current_user
from app.crud import category as category_crud

router = APIRouter()

@router.post("/", response_model=CategoryResponse)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new category for the logged-in user
    """
    # Check if category name already exists for this user
    existing = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == category_in.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    category = Category(
        name=category_in.name,
        type=category_in.type,
        user_id=current_user.id
    )

    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all categories for the logged-in user.
    """
    return category_crud.get_user_categories(db, current_user.id)
