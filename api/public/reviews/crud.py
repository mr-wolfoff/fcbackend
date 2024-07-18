from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlmodel import select

from api.public.reviews.models import Review, ReviewCreate, ReviewUpdate, ReviewRead
from api.public.user.models import User
from api.database import get_session


def create_review(review: ReviewCreate, db: Session = Depends(get_session)):
    review_to_db = Review(**review.dict())
    db.add(review_to_db)
    db.commit()
    db.refresh(review_to_db)
    return review_to_db


def read_reviews(offset: int = 0, limit: int = 20, db: Session = Depends(get_session)) -> List[ReviewRead]:
    reviews = db.exec(select(Review).offset(offset).limit(limit)).all()
    return [ReviewRead.from_orm(review) for review in reviews]


def read_review(review_id: int, db: Session = Depends(get_session)) -> Review:
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review not found with id: {review_id}",
        )
    return review


def update_review(review_id: int, review: ReviewUpdate, db: Session = Depends(get_session)) -> Review:
    review_to_update = db.get(Review, review_id)
    if not review_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review not found with id: {review_id}",
        )

    review_data = review.dict(exclude_unset=True)
    for key, value in review_data.items():
        setattr(review_to_update, key, value)

    db.add(review_to_update)
    db.commit()
    db.refresh(review_to_update)
    return review_to_update


def delete_review(review_id: int, db: Session = Depends(get_session)):
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review not found with id: {review_id}",
        )
    db.delete(review)
    db.commit()
    return {"ok": True}


def get_reviews_received_by_user(user_id: int, db: Session = Depends(get_session)) -> List[ReviewRead]:
    reviews = db.exec(select(Review).where(Review.user_id_to == user_id)).all()
    return [ReviewRead.from_orm(review) for review in reviews]


def get_reviews_given_by_user(user_id: int, db: Session = Depends(get_session)) -> List[ReviewRead]:
    reviews = db.exec(select(Review).where(Review.user_id_from == user_id)).all()
    return [ReviewRead.from_orm(review) for review in reviews]
