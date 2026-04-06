from decimal import Decimal
from sqlalchemy import func

from app.models.transaction import Transaction
from app.models.enums import TransactionType

OVERALL_CATEGORY_NAMES = {"general", "overall", "all expenses"}


def _is_overall_budget(budget):
    if len(budget.budget_categories) != 1:
        return False

    category = budget.budget_categories[0].category
    if not category or not category.name:
        return False

    return category.name.strip().lower() in OVERALL_CATEGORY_NAMES


def calculate_budget_usage(db, budget):
    if _is_overall_budget(budget):
        budget_category = budget.budget_categories[0]
        total_spent = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id == budget.user_id,
                Transaction.type == TransactionType.expense,
                Transaction.transaction_date >= budget.start_date,
                Transaction.transaction_date <= budget.end_date
            )
            .scalar()
        )

        spent_amount = Decimal(str(total_spent))
        budget_category.spent_amount = spent_amount
        budget_category.remaining_amount = (
            budget_category.allocated_amount - spent_amount
        )

        if budget_category.allocated_amount > 0:
            budget_category.usage_percentage = round(
                float(spent_amount / budget_category.allocated_amount * 100),
                2
            )
        else:
            budget_category.usage_percentage = 0.0

        budget.spent_amount = spent_amount
        budget.remaining_amount = budget.amount - spent_amount

        if budget.amount > 0:
            budget.usage_percentage = round(
                float(spent_amount / budget.amount * 100),
                2
            )
        else:
            budget.usage_percentage = 0.0

        if budget.usage_percentage >= 100:
            budget.status = "exceeded"
        elif budget.status == "cancelled":
            budget.status = "cancelled"
        else:
            budget.status = "active"

        return budget

    spent_amount = Decimal("0.00")

    for budget_category in budget.budget_categories:
        category_spent = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id == budget.user_id,
                Transaction.category_id == budget_category.category_id,
                Transaction.type == TransactionType.expense,
                Transaction.transaction_date >= budget.start_date,
                Transaction.transaction_date <= budget.end_date
            )
            .scalar()
        )

        category_spent = Decimal(str(category_spent))

        budget_category.spent_amount = category_spent
        budget_category.remaining_amount = (
            budget_category.allocated_amount - category_spent
        )

        if budget_category.allocated_amount > 0:
            budget_category.usage_percentage = round(
                float(category_spent / budget_category.allocated_amount * 100),
                2
            )
        else:
            budget_category.usage_percentage = 0.0

        spent_amount += category_spent

    budget.spent_amount = spent_amount
    budget.remaining_amount = budget.amount - spent_amount

    if budget.amount > 0:
        budget.usage_percentage = round(
            float(spent_amount / budget.amount * 100),
            2
        )
    else:
        budget.usage_percentage = 0.0

    if budget.usage_percentage >= 100:
        budget.status = "exceeded"
    elif budget.status == "cancelled":
        budget.status = "cancelled"
    else:
        budget.status = "active"

    return budget
