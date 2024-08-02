import uuid
from typing import Any, List
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select
from app.api.deps import CurrentUser, SessionDep
from app.models import Listing, ListingCreate, ListingPublic, ListingsPublic, ListingUpdate, Message, ListingSearch

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
    session: SessionDep = SessionDep,
    current_user: CurrentUser = CurrentUser,
) -> Any:
    """
    Create new listing.
    """
    new_listing = Listing.model_validate(listing, update={"owner_id": current_user.id})
    session.add(new_listing)
    session.commit()
    session.refresh(new_listing)
    return new_listing

@router.get("/{listing_id}", response_model=ListingPublic)
def read_listing(
    listing_id: uuid.UUID,
    session: SessionDep = SessionDep,
    current_user: CurrentUser = CurrentUser,
) -> Any:
    """
    Get a listing by ID.
    """
    db_listing = session.get(Listing, listing_id)
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not current_user.is_superuser and db_listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_listing

@router.put("/{listing_id}", response_model=ListingPublic)
def update_listing(
    listing_id: uuid.UUID,
    listing: ListingUpdate,
    session: SessionDep = SessionDep,
    current_user: CurrentUser = CurrentUser,
) -> Any:
    """
    Update a listing by ID.
    """
    db_listing = session.get(Listing, listing_id)
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not current_user.is_superuser and db_listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    updated = listing.model_dump(exclude_unset=True)
    db_listing.sqlmodel_update(updated)
    session.add(db_listing)
    session.commit()
    session.refresh(db_listing)
    return db_listing    

@router.delete("/{listing_id}", response_model=ListingPublic)
def delete_listing(
    listing_id: uuid.UUID,
    session: SessionDep = SessionDep,
    current_user: CurrentUser = CurrentUser,
) -> Any:
    """
    Delete a listing by ID.
    """
    db_listing = session.get(Listing, listing_id)
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not current_user.is_superuser and db_listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(db_listing)
    session.commit()
    return Message(message="Listing deleted successfully")

@router.post("/search", response_model=List[ListingPublic])
def search_listings(
    search_query: ListingSearch,
    db: SessionDep = SessionDep
) -> List[ListingPublic]:
    query = select(Listing)

    if search_query.title:
        query = query.where(Listing.title.contains(search_query.title))
    if search_query.category:
        query = query.where(Listing.category == search_query.category)
    if search_query.location:
        query = query.where(Listing.location == search_query.location)
    if search_query.min_price is not None:
        query = query.where(Listing.price >= search_query.min_price)
    if search_query.max_price is not None:
        query = query.where(Listing.price <= search_query.max_price)

    listings = db.exec(query).all()

    if not listings:
        raise HTTPException(status_code=404, detail="No listings found")

    return listings