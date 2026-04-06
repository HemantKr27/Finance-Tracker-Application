from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.category import Category
from app.schemas.transaction import TransactionCreate

def create_transaction(db: Session, transaction: TransactionCreate, user_id:int):
    account = db.query(Account).filter(
        Account.id == transaction.account_id,
        Account.user_id == user_id
        ).first()

    category = db.query(Category).filter(
        Category.id == transaction.category_id,
        Category.user_id == user_id
    ).first()
    
    if not account or not category:
        return None
    db_transaction = Transaction(
        amount=transaction.amount,
        type=category.type,
        description=transaction.description,
        account_id=transaction.account_id,
        category_id=transaction.category_id,
        user_id=user_id
        )
    
    if category.type == "expense":
        account.balance -= transaction.amount
    elif category.type == "income":
        account.balance += transaction.amount
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions_by_user(db: Session, user_id: int):
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()



from app.models.transaction import Transaction
from app.models.account import Account


def delete_transaction(db: Session, transaction_id: int, user_id: int):
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
        .first()
    )

    if not transaction:
        return None

    account = (
        db.query(Account)
        .filter(Account.id == transaction.account_id)
        .first()
    )

    if account:
        if transaction.type == "expense":
            account.balance += transaction.amount
        elif transaction.type == "income":
            account.balance -= transaction.amount

    db.delete(transaction)
    db.commit()

    return transaction
