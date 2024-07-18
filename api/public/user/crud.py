from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

# from api.database import get_session
from api.public.user.models import User, UserCreate, UserUpdate, UserRead


def create_user(user: UserCreate, db: Session = None):
    user_to_db = User.model_validate(user)
    db.add(user_to_db)
    db.commit()
    db.refresh(user_to_db)
    return user_to_db


def read_users(offset: int = 0, limit: int = 20, db: Session = None):
    users = db.exec(select(User).offset(offset).limit(limit)).all()
    # return users
    return [UserRead.from_orm(user) for user in users]


def read_user(user_id: int, db: Session = None):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with id: {user_id}",
        )
    return user

def reset_user(db: Session, user: User):
    user = db.get(User, user.id)
    user.is_accepted = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def read_user_by_email(email: str, db: Session = None):
    statement = select(User).where(User.email == email)
    user = db.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with email: {email}",
        )
    return user


def update_user(user_id: int, user: UserUpdate, db: Session = None):
    user_to_update = db.get(User, user_id)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with id: {user_id}",
        )

    user_data = user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user_to_update, key, value)

    db.add(user_to_update)
    db.commit()
    db.refresh(user_to_update)
    return user_to_update


def delete_user(user_id: int, db: Session = None):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with id: {user_id}",
        )
    db.delete(user)
    db.commit()
    return {"ok": True}