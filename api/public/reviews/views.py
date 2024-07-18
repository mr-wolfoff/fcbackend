from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from api.database import get_session
from api.public.reviews.crud import create_review, read_reviews, read_review, update_review, delete_review
from api.public.reviews.models import ReviewCreate, ReviewRead, ReviewUpdate, Review

router = APIRouter()


@router.post("/reviews/", response_model=ReviewRead)
def create_review_endpoint(review: ReviewCreate, db: Session = Depends(get_session)):
    """
    Создание нового отзыва.
    """
    return create_review(review, db=db)


@router.get("/reviews/", response_model=List[ReviewRead])
def read_reviews_endpoint(offset: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    """
    Получение списка отзывов с пагинацией.
    """
    return read_reviews(offset=offset, limit=limit, db=db)


@router.get("/reviews/{review_id}", response_model=ReviewRead)
def read_review_endpoint(review_id: int, db: Session = Depends(get_session)):
    """
    Получение конкретного отзыва по его идентификатору.
    """
    return read_review(review_id, db=db)


@router.put("/reviews/{review_id}", response_model=ReviewRead)
def update_review_endpoint(review_id: int, review: ReviewUpdate, db: Session = Depends(get_session)):
    """
    Обновление существующего отзыва.
    """
    return update_review(review_id, review, db=db)


@router.delete("/reviews/{review_id}")
def delete_review_endpoint(review_id: int, db: Session = Depends(get_session)):
    """
    Удаление отзыва по его идентификатору.
    """
    return delete_review(review_id, db=db)
