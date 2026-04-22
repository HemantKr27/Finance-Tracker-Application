from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.dependencies import get_db
from app.models.user import User
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.models.category import Category
from app.api.deps import get_current_user
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from app.services.budget_service import calculate_budget_usage
from app.models.transaction import Transaction
from sqlalchemy import func
router = APIRouter()


# -----------------------------
# CREATE BUDGET
# -----------------------------
@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check for existing active budget in same period
    existing_budget = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            Budget.name == budget_data.name,
            Budget.period == budget_data.period,
            #Budget.start_date == budget_data.start_date,
            #Budget.end_date == budget_data.end_date,
            Budget.status == "active"
        )
        .first()
    )
    if existing_budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active budget already exists for this period"
        )

    # Create Budget
    budget = Budget(
        user_id=current_user.id,
        name=budget_data.name,
        period=budget_data.period,
        amount=budget_data.amount,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        threshold_percentage=budget_data.threshold_percentage,
        is_recurring=budget_data.is_recurring,
        status=budget_data.status,
    )
    db.add(budget)
    db.flush()  # so budget.id is available

    # Add categories
    for cat_data in budget_data.categories:
        category = db.query(Category).filter(Category.id == cat_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Category with id {cat_data.category_id} not found")

        budget_category = BudgetCategory(
            budget_id=budget.id,
            category_id=cat_data.category_id,
            allocated_amount=cat_data.allocated_amount,
            alert_percentage=cat_data.alert_percentage
        )
        db.add(budget_category)

    db.commit()
    db.refresh(budget)

    # Calculate usage dynamically (all zeros initially)
    calculate_budget_usage(db, budget)

    return budget


# -----------------------------
# UPDATE BUDGET
# -----------------------------
@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == current_user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    # Update budget fields
    for field, value in budget_data.dict(exclude_unset=True).items():
        setattr(budget, field, value)

    db.commit()
    db.refresh(budget)

    # Recalculate usage after update
    calculate_budget_usage(db, budget)

    return budget


# -----------------------------
# GET ALL BUDGETS
# -----------------------------
@router.get("/", response_model=list[BudgetResponse])
def get_budgets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    budgets = (
        db.query(Budget)
        .options(joinedload(Budget.budget_categories).joinedload(BudgetCategory.category))
        .filter(Budget.user_id == current_user.id)
        .order_by(Budget.start_date.desc())
        .all()
    )

    for budget in budgets:
        calculate_budget_usage(db, budget)

    return budgets


# -----------------------------
# GET BUDGET BY ID
# -----------------------------
@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget_by_id(budget_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    budget = (
        db.query(Budget)
        .options(joinedload(Budget.budget_categories).joinedload(BudgetCategory.category))
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    calculate_budget_usage(db, budget)

    return budget

