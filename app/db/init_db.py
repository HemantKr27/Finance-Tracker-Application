from app.db.base import Base
from app.db.session import engine

# Import all models here so SQLAlchemy sees them
from app.models.user import User
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget


def init_db():
    Base.metadata.create_all(bind=engine)