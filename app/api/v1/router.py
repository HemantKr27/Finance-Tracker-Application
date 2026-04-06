from fastapi import APIRouter
from .endpoints import auth, user, account, transaction, category, budget

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(user.router, prefix="/users", tags=["users"])
router.include_router(account.router, prefix="/accounts", tags=["accounts"])
router.include_router(transaction.router, prefix="/transactions",tags=["transactions"])
router.include_router(category.router, prefix="/categories", tags=["categories"])
router.include_router(budget.router, prefix="/budgets", tags=["budgets"])