'''from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.dependencies import get_db
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.models.category import Category
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from app.api.deps import get_current_user
from app.services.budget_service import calculate_budget_usage

router = APIRouter()    


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_allocated = sum(
        category.allocated_amount for category in budget_data.categories
    )

    if total_allocated > budget_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total category allocation cannot exceed budget amount"
        )

    existing_budget = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            Budget.period == budget_data.period,
            Budget.start_date == budget_data.start_date,
            Budget.end_date == budget_data.end_date,
            Budget.status == "active"
        )
        .first()
    )

    if existing_budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active budget already exists for this period"
        )

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
    db.flush()

    for category_data in budget_data.categories:
        category_exists = (
            db.query(Category)
            .filter(Category.id == category_data.category_id)
            .first()
        )

        if not category_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_data.category_id} not found"
            )

        budget_category = BudgetCategory(
            budget_id=budget.id,
            category_id=category_data.category_id,
            allocated_amount=category_data.allocated_amount,
            alert_percentage=category_data.alert_percentage,
        )

        db.add(budget_category)

    db.commit()
    db.refresh(budget)

    return (
        db.query(Budget)
        .options(joinedload(Budget.budget_categories))
        .filter(Budget.id == budget.id)
        .first()
    )


@router.get("/", response_model=list[BudgetResponse])
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budgets = (
        db.query(Budget)
        .options(
            joinedload(Budget.budget_categories)
        )
        .filter(Budget.user_id == current_user.id)
        .order_by(Budget.start_date.desc())
        .all()
    )

    calculated_budgets = []

    for budget in budgets:
        calculated_budgets.append(calculate_budget_usage(db, budget))

    return calculated_budgets


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget_by_id(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = (
        db.query(Budget)
        .options(
            joinedload(Budget.budget_categories)
        )
        .filter(
            Budget.id == budget_id,
            Budget.user_id == current_user.id
        )
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    return calculate_budget_usage(db, budget)



@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = (
        db.query(Budget)
        .options(joinedload(Budget.budget_categories))
        .filter(
            Budget.id == budget_id,
            Budget.user_id == current_user.id
        )
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    update_data = budget_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(budget, field, value)

    if budget.start_date and budget.end_date:
        if budget.end_date < budget.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_date must be greater than or equal to start_date"
            )

    db.commit()
    db.refresh(budget)

    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = (
        db.query(Budget)
        .filter(
            Budget.id == budget_id,
            Budget.user_id == current_user.id
        )
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    db.delete(budget)
    db.commit()


@router.get("/", response_model=list[BudgetResponse])
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Load all budgets of the user, including categories
    budgets = (
        db.query(Budget)
        .options(joinedload(Budget.budget_categories).joinedload("category"))
        .filter(Budget.user_id == current_user.id)
        .order_by(Budget.start_date.desc())
        .all()
    )

    # Calculate spent_amount, remaining_amount, and usage_percentage dynamically
    for budget in budgets:
        calculate_budget_usage(db, budget)

    return budgets


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget_by_id(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = (
        db.query(Budget)
        .options(joinedload(Budget.budget_categories).joinedload("category"))
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    # Calculate usage for this single budget
    calculate_budget_usage(db, budget)

    return budget'''



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.dependencies import get_db
from app.models.user import User
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.models.category import Category
from app.api.deps import get_current_user
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from app.services.budget_service import OVERALL_CATEGORY_NAMES, calculate_budget_usage
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
    category_records = []
    total_allocated = sum(
        category.allocated_amount for category in budget_data.categories
    )

    for cat_data in budget_data.categories:
        category = (
            db.query(Category)
            .filter(
                Category.id == cat_data.category_id,
                Category.user_id == current_user.id
            )
            .first()
        )
        if not category:
            raise HTTPException(status_code=404, detail=f"Category with id {cat_data.category_id} not found")
        category_records.append((cat_data, category))

    overall_categories = [
        category for _, category in category_records
        if category.name and category.name.strip().lower() in OVERALL_CATEGORY_NAMES
    ]
    if overall_categories and len(category_records) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A General/Overall budget cannot be combined with other category allocations"
        )

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
        amount=total_allocated,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        threshold_percentage=budget_data.threshold_percentage,
        is_recurring=budget_data.is_recurring,
        status=budget_data.status,
    )
    db.add(budget)
    db.flush()  # so budget.id is available

    # Add categories
    for cat_data, category in category_records:
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
    for field, value in budget_data.model_dump(exclude_unset=True).items():
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
    

'''@router.get("/budgets")
def get_user_budgets(user_id: int, db: Session = Depends(get_db)):
    """
    Returns all budgets for a user with dynamically calculated:
    - spent_amount
    - remaining_amount
    - percentage_used
    """
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    result = []

    for budget in budgets:
        categories_data = []
        for bc in budget.budget_categories:
            # Calculate spent amount for this budget category
            spent = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.category_id == bc.category_id,
                Transaction.transaction_date >= budget.start_date,
                Transaction.transaction_date <= budget.end_date,
                Transaction.user_id == user_id
            ).scalar()

            remaining = float(bc.allocated_amount) - float(spent)
            percentage_used = (float(spent) / float(bc.allocated_amount) * 100) if bc.allocated_amount > 0 else 0

            categories_data.append({
                "budget_category_id": bc.id,
                "category_id": bc.category_id,
                "allocated_amount": float(bc.allocated_amount),
                "spent_amount": float(spent),
                "remaining_amount": float(remaining),
                "percentage_used": round(percentage_used, 2)
            })

        # Budget totals
        total_allocated = sum(cd["allocated_amount"] for cd in categories_data)
        total_spent = sum(cd["spent_amount"] for cd in categories_data)
        total_remaining = total_allocated - total_spent
        total_percentage = (total_spent / total_allocated * 100) if total_allocated > 0 else 0

        result.append({
            "budget_id": budget.id,
            "name": budget.name,
            "amount": float(budget.amount),
            "start_date": budget.start_date,
            "end_date": budget.end_date,
            "spent_amount": round(total_spent, 2),
            "remaining_amount": round(total_remaining, 2),
            "percentage_used": round(total_percentage, 2),
            "categories": categories_data
        })

    return {"budgets": result}
    '''
