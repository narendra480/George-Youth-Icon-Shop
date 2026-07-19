from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.authorization import require_authentication
from app.db.session import get_db
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.db.models import Review
from app.db.models import User

router = APIRouter(tags=["Reviews"])


@router.get("/reviews", response_model=list[ReviewResponse])
def list_all_reviews(db: Session = Depends(get_db), is_active: Optional[bool] = None, limit: Optional[int] = None):
    query = db.query(Review)
    if is_active is not None:
        query = query.filter(Review.is_active == is_active)
    if limit:
        query = query.limit(limit)
    return query.order_by(Review.created_at.desc()).all()


@router.get("/products/{product_id}/reviews", response_model=list[ReviewResponse])
def list_reviews(product_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.product_id == product_id, Review.is_active == True).all()


@router.post("/products/{product_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(product_id: int, payload: ReviewCreate, db: Session = Depends(get_db), user: User = Depends(require_authentication)):
    review = Review(product_id=product_id, user_id=user.id, **payload.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.put("/products/reviews/{review_id}", response_model=ReviewResponse)
def update_review(review_id: int, payload: ReviewUpdate, db: Session = Depends(get_db), user: User = Depends(require_authentication)):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == user.id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(review, key, value)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/products/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Session = Depends(get_db), user: User = Depends(require_authentication)):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == user.id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    review.is_active = False
    db.commit()