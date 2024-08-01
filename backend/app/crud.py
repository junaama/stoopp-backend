import uuid
from typing import Any, List

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate, Listing, ListingCreate, ListingUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

# def get_listing(db: Session, listing_id: int) -> Listing:
#     return db.get(Listing, listing_id)

# def get_listings(db: Session, skip: int = 0, limit: int = 10) -> List[Listing]:
#     listings = db.exec(select(Listing).offset(skip).limit(limit)).all()
#     return listings

# def create_listing(db: Session, listing: ListingCreate) -> Listing:
#     db_listing = Listing.from_orm(listing)
#     db.add(db_listing)
#     db.commit()
#     db.refresh(db_listing)
#     return db_listing

# def update_listing(db: Session, listing_id: int, listing: ListingUpdate) -> Listing:
#     db_listing = db.get(Listing, listing_id)
#     if not db_listing:
#         return None
#     for key, value in listing.dict(exclude_unset=True).items():
#         setattr(db_listing, key, value)
#     db.add(db_listing)
#     db.commit()
#     db.refresh(db_listing)
#     return db_listing

# def delete_listing(db: Session, listing_id: int) -> Listing:
#     db_listing = db.get(Listing, listing_id)
#     if not db_listing:
#         return None
#     db.delete(db_listing)
#     db.commit()
#     return db_listing


def get_listing(db: Session, listing_id: uuid.UUID) -> Listing:
    return db.get(Listing, listing_id)

def get_listings(db: Session, owner_id: uuid.UUID = None, skip: int = 0, limit: int = 10) -> List[Listing]:
    statement = select(Listing).offset(skip).limit(limit)
    if owner_id:
        statement = statement.where(Listing.owner_id == owner_id)
    return db.exec(statement).all()

def create_listing(db: Session, listing: ListingCreate, owner_id: uuid.UUID) -> Listing:
    db_listing = Listing.from_orm(listing)
    db_listing.owner_id = owner_id
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def update_listing(db: Session, listing_id: uuid.UUID, listing: ListingUpdate) -> Listing:
    db_listing = db.get(Listing, listing_id)
    if not db_listing:
        return None
    for key, value in listing.dict(exclude_unset=True).items():
        setattr(db_listing, key, value)
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def delete_listing(db: Session, listing_id: uuid.UUID) -> Listing:
    db_listing = db.get(Listing, listing_id)
    if not db_listing:
        return None
    db.delete(db_listing)
    db.commit()
    return db_listing

def get_transaction(db: Session, transaction_id: uuid.UUID) -> Optional[Transaction]:
    return db.get(Transaction, transaction_id)

def get_transactions(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 10) -> List[Transaction]:
    statement = (
        select(Transaction)
        .where((Transaction.renter_id == user_id) | (Transaction.lender_id == user_id))
        .offset(skip)
        .limit(limit)
    )
    return db.exec(statement).all()

def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
    db_transaction = Transaction.from_orm(transaction)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: uuid.UUID, transaction: TransactionUpdate) -> Optional[Transaction]:
    db_transaction = db.get(Transaction, transaction_id)
    if not db_transaction:
        return None
    for key, value in transaction.dict(exclude_unset=True).items():
        setattr(db_transaction, key, value)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: uuid.UUID) -> Optional[Transaction]:
    db_transaction = db.get(Transaction, transaction_id)
    if not db_transaction:
        return None
    db.delete(db_transaction)
    db.commit()
    return db_transaction