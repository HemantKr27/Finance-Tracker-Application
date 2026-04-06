import enum

class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"

class BudgetPeriod(str, enum.Enum):
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"

class BudgetStatus(str, enum.Enum):
    active = "active"
    exceeded = "exceeded"
    completed = "completed"
    cancelled = "cancelled"