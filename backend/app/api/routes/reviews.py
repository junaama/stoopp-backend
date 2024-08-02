import uuid
from typing import List

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import ReviewPublic, ReviewCreate, Review

router = APIRouter()

@router.post("/", response_model=ReviewPublic)
def create_review(
    review: ReviewCreate,
    db: SessionDep,
    current_user: CurrentUser
) -> ReviewPublic:
    db_review = Review.model_validate(review, update={"reviewer_id": current_user.id})
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@router.get("/listing/{listing_id}", response_model=List[ReviewPublic])
def get_reviews_for_listing(
    listing_id: uuid.UUID,
    db: SessionDep
) -> List[ReviewPublic]:
    query = select(Review).where(Review.listing_id == listing_id)
    reviews = db.exec(query).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this listing")
    return reviews

@router.get("/user/{user_id}", response_model=List[ReviewPublic])
def get_reviews_for_user(
    user_id: uuid.UUID,
    db: SessionDep,
) -> List[ReviewPublic]:
    query = select(Review).where(Review.reviewee_id == user_id)
    reviews = db.exec(query).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this user")
    return reviews