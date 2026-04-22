from sqlalchemy.orm import Session, joinedload

from app.models.budget import Budget, BudgetCategory
from app.models.category import Category
from app.schemas.budget import BudgetCreate


def create_budget(
    db: Session,
    user_id: int,
    budget_data: BudgetCreate
):
    total_allocated = sum(
        category.allocated_amount for category in budget_data.categories
    )

    if total_allocated > budget_data.amount:
        raise ValueError("Total category allocation cannot exceed total budget")

    existing_budget = (
        db.query(Budget)
        .filter(
            Budget.user_id == user_id,
            Budget.period_type == budget_data.period,
            Budget.start_date == budget_data.start_date,
            Budget.end_date == budget_data.end_date,
            Budget.status == "active"
        )
        .first()
    )

    if existing_budget:
        raise ValueError("An active budget already exists for this period")

    budget = Budget(
        user_id=user_id,
        name=budget_data.name,
        period_type=budget_data.period,
        total_budget=budget_data.amount,
        currency=budget_data.currency,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        is_recurring=budget_data.is_recurring,
        status=budget_data.status
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
            raise ValueError(
                f"Category with id {category_data.category_id} not found"
            )

        budget_category = BudgetCategory(
            budget_id=budget.id,
            category_id=category_data.category_id,
            allocated_amount=category_data.allocated_amount,
            alert_percentage=category_data.alert_percentage
        )

        db.add(budget_category)

    db.commit()
    db.refresh(budget)

    return budget