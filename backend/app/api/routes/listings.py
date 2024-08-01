import uuid
from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import func, select
from sqlalchemy.orm import Session
from app.api.deps import CurrentUser, SessionDep
from app.models import Listing, ListingCreate, ListingPublic, ListingsPublic, ListingUpdate, Message
from app.crud import crud_listing

router = APIRouter()

@router.get("/", response_model=ListingsPublic)
def read_listings(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve listings.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Listing)
        count = session.exec(count_statement).one()
        statement = select(Listing).offset(skip).limit(limit)
        listings = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Listing)
            .where(Listing.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Listing)
            .where(Listing.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        listings = session.exec(statement).all()

    return ListingsPublic(data=listings, count=count)

@router.post("/", response_model=ListingPublic)
def create_listing(
    listing: ListingCreate,
    session: SessionDep = Depends(),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Create new listing.
    """
    return crud_listing.create_listing(session, listing, current_user.id)

@router.get("/{listing_id}", response_model=ListingPublic)
def read_listing(
    listing_id: uuid.UUID,
    session: SessionDep = Depends(),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Get a listing by ID.
    """
    db_listing = crud_listing.get_listing(session, listing_id)
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not current_user.is_superuser and db_listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_listing

@router.put("/{listing_id}", response_model=ListingPublic)
def update_listing(
    listing_id: uuid.UUID,
    listing: ListingUpdate,
    session: SessionDep = Depends(),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Update a listing by ID.
    """
    db_listing = crud_listing.get_listing(session, listing_id)
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not current_user.is_superuser and db_listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_listing.update_listing(session, listing_id, listing)

@router.delete("/{listing_id}", response_model=ListingPublic)
def delete_listing(
    listing_id: uuid.UUID,
    session: SessionDep = Depends(),
    current_user: CurrentUser = Depends(),
) -> Any:
    """
    Delete a listing by ID.
    """
    db_listing = crud_listing.get_listing(session, listing_id)
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not current_user.is_superuser and db_listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_listing.delete_listing(session, listing_id)
