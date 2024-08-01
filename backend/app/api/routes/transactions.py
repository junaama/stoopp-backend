import uuid
from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.deps import CurrentUser, SessionDep
from app.models import Transaction, TransactionCreate, TransactionPublic, TransactionsPublic, TransactionUpdate
from app.crud import crud_transaction

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
    session: SessionDep = Depends(),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Create a new transaction.
    """
    return crud_transaction.create_transaction(session, transaction)

@router.get("/{transaction_id}", response_model=TransactionPublic)
def read_transaction(
    transaction_id: uuid.UUID,
    session: SessionDep = Depends(),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Get a transaction by ID.
    """
    db_transaction = crud_transaction.get_transaction(session, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not current_user.is_superuser and db_transaction.renter_id != current_user.id and db_transaction.lender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_transaction

@router.put("/{transaction_id}", response_model=TransactionPublic)
def update_transaction(
    transaction_id: uuid.UUID,
    transaction: TransactionUpdate,
    session: SessionDep = Depends(),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Update a transaction by ID.
    """
    db_transaction = crud_transaction.get_transaction(session, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not current_user.is_superuser and db_transaction.renter_id != current_user.id and db_transaction.lender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_transaction.update_transaction(session, transaction_id, transaction)

@router.delete("/{transaction_id}", response_model=TransactionPublic)
def delete_transaction(
    transaction_id: uuid.UUID,
    session: SessionDep = Depends(),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Delete a transaction by ID.
    """
    db_transaction = crud_transaction.get_transaction(session, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not current_user.is_superuser and db_transaction.renter_id != current_user.id and db_transaction.lender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_transaction.delete_transaction(session, transaction_id)
