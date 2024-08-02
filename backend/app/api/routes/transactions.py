import uuid
from typing import Any
from fastapi import APIRouter, HTTPException
from app.api.deps import CurrentUser, SessionDep
from app.models import Transaction, TransactionCreate, TransactionPublic, TransactionsPublic, TransactionUpdate, Message
from sqlmodel import func, select

router = APIRouter()

@router.get("/", response_model=TransactionsPublic)
def read_transactions(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve transactions for the current user.
    """
    count_statement = (
        select(func.count())
        .select_from(Transaction)
        .where((Transaction.renter_id == current_user.id) | (Transaction.lender_id == current_user.id))
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Transaction)
        .where((Transaction.renter_id == current_user.id) | (Transaction.lender_id == current_user.id))
        .offset(skip)
        .limit(limit)
    )
    transactions = session.exec(statement).all()

    return TransactionsPublic(data=transactions, count=count)

@router.post("/", response_model=TransactionPublic)
def create_transaction(
    transaction: TransactionCreate,
    session: SessionDep = SessionDep,
    current_user: CurrentUser = CurrentUser,
) -> Any:
    """
    Create a new transaction.
    """
    new_transaction = Transaction.model_validate(transaction, update={"owner_id":current_user.id})
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)
    return new_transaction

@router.get("/{transaction_id}", response_model=TransactionPublic)
def read_transaction(
    transaction_id: uuid.UUID,
    session: SessionDep = SessionDep,
    current_user: CurrentUser = CurrentUser,
) -> Any:
    """
    Get a transaction by ID.
    """
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not current_user.is_superuser and db_transaction.renter_id != current_user.id and db_transaction.lender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_transaction

@router.put("/{transaction_id}", response_model=TransactionPublic)
def update_transaction(
    transaction_id: uuid.UUID,
    transaction: TransactionUpdate,
    session: SessionDep = SessionDep,
    current_user: CurrentUser = CurrentUser,
) -> Any:
    """
    Update a transaction by ID.
    """
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not current_user.is_superuser and db_transaction.renter_id != current_user.id and db_transaction.lender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    updated = transaction.model_dump(exclude_unset=True)
    db_transaction.sqlmodel_update(updated)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

@router.delete("/{transaction_id}", response_model=TransactionPublic)
def delete_transaction(
    transaction_id: uuid.UUID,
    session: SessionDep = SessionDep,
    current_user: CurrentUser = CurrentUser,
) -> Any:
    """
    Delete a transaction by ID.
    """
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not current_user.is_superuser and db_transaction.renter_id != current_user.id and db_transaction.lender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(db_transaction)
    session.commit()
    return Message(message="Item deleted successfully")