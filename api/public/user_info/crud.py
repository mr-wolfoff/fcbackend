from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status, UploadFile
from sqlmodel import Session, select, and_, or_, not_

from api.auth import current_active_user
from api.database import get_session
from api.public.user_info.models import UserInfo, UserInfoCreate, UserInfoUpdate, UserInfoRead, TGFromUser, UserInfoBase
from api.public.user.models import UserCreate, User
from api.public.user.crud import create_user
from backend_services.aws_interaction import upload_file_to_s3_from_api


def create_user_info(user: UserInfoCreate, db: Session):
    user_info_to_db = UserInfo.model_validate(user)
    db.add(user_info_to_db)
    db.commit()
    db.refresh(user_info_to_db)
    return user_info_to_db


def update_user_picture(user: User, file: UploadFile, db: Session) -> dict:
    file_link = upload_file_to_s3_from_api(file, aws_file_name=f'{user.id}_user_picture_{file.filename}')
    user_info = db.get(UserInfo, user.id)
    if not user_info:
        user_info = UserInfo(user_id=user.id)
    user_info.picture_url = file_link
    db.add(user_info)
    db.commit()
    db.refresh(user_info)
    return {"link": file_link}


def read_user_info(user_id: str, db: Session):
    user = db.get(UserInfo, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User Info not found with id: {user_id}",
        )
    return user

def read_my_user_info(db: Session, current_user: User):
    user_info = db.get(UserInfo, current_user.id)
    if not user_info:
        user_info = UserInfo(user_id=current_user.id)
        db.add(user_info)
        db.commit()
        db.refresh(user_info)
    return user_info

def read_user_info_by_tg_id(tg_from_user: TGFromUser, db: Session):
    statement = select(UserInfo).where(UserInfo.tg_id == tg_from_user.id)
    user_info = db.exec(statement).first()
    if not user_info:
        user = create_user(UserCreate(), db=db)
        user_info = create_user_info(UserInfoCreate(user_id=user.user_id, tg_id=tg_from_user.id,
                                                    tg_first_name=tg_from_user.first_name,
                                                    tg_last_name=tg_from_user.last_name,
                                                    tg_username=tg_from_user.username)
                                     , db=db)
    return user_info


def update_user_info(user_id: int, user: UserInfoUpdate, db: Session):
    user_to_update = db.get(UserInfo, user_id)
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

def update_my_user_info(user_info: UserInfoUpdate, db: Session = Depends(get_session),
                        user: User = Depends(current_active_user)):
    user_info_to_update = db.get(UserInfo, user.id)
    if user_info_to_update is None:
        user_info_to_update = UserInfo(user_id=user.id, user=user)
    user_data = user_info.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user_info_to_update, key, value)
    db.add(user_info_to_update)
    db.commit()
    db.refresh(user_info_to_update)
    return user_info_to_update


def delete_user_info(user_id: int, db: Session):
    user = db.get(UserInfo, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with id: {user_id}",
        )
    db.delete(user)
    db.commit()
    return {"ok": True}

def get_user_who_want_to_rent_in_a_country(country: str, db: Session):
    statement = select(UserInfo).where(and_(UserInfo.where_to_rent.ilike('%' + country.lower() + '%'),
                                            UserInfo.where_to_rent != 'нет',
                                            UserInfo.where_to_rent != 'Нет'))
    user_infos = db.exec(statement).all()
    return user_infos


def read_users_unfinished_onboarding(db: Session):
    statement = select(UserInfo, User).where(and_(UserInfo.user_id == User.id,
                                                  or_(UserInfo.onboarding_completed == False,
                                                      UserInfo.onboarding_completed.is_(None)),  # not completed onboarding
                                                  UserInfo.created_at > datetime(2024, 2, 4),
                                                  UserInfo.blocked_timestamp.is_(None),  # Not blocked
                                                  UserInfo.tg_id.isnot(None),
                                                  or_(User.is_accepted.is_(None), User.is_accepted != True),  # Not accepted
                                                  User.premium_until.is_(None),  # NO premium
                                        ))

    user_infos: [UserInfo, User] = db.exec(statement).all()
    return user_infos

def read_users_ended_access(db: Session):
    statement = select(UserInfo, User).where(and_(UserInfo.user_id == User.id,
                                                  or_(UserInfo.onboarding_completed == False,
                                                      UserInfo.onboarding_completed.is_(None)),  # not completed onboarding
                                                  User.is_accepted,
                                                  User.premium_until <= datetime.utcnow(),
                                                  User.created_at > datetime(2024, 5, 24),
                                                  UserInfo.tg_id.isnot(None),
                                        ))
    user_infos: [UserInfo, User] = db.exec(statement).all()
    return user_infos




def read_users_for_pushes(db: Session):
    statement = select(UserInfo).where(and_(UserInfo.notifications,
                                            not_(UserInfo.where_to_let.ilike('нет')),
                                            not_(UserInfo.where_to_let.ilike('не знаю')),
                                            )
                                       )
    user_infos = db.exec(statement).all()
    return user_infos


