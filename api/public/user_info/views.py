from typing import List

from fastapi import APIRouter, Depends, Query, File, UploadFile
from pydantic import UUID4
from sqlmodel import Session

from api.auth import current_active_user, current_accepted_user, current_superuser
from api.database import get_session
from api.public.user.models import User, UserRead
from api.public.user_info.crud import (
    create_user_info,
    delete_user_info,
    read_user_info,
    update_user_info,
    read_user_info_by_tg_id, update_user_picture, read_my_user_info, update_my_user_info,
    get_user_who_want_to_rent_in_a_country, read_users_unfinished_onboarding, read_users_for_pushes,
    read_users_ended_access,
)
from api.public.user_info.models import UserInfoCreate, UserInfoRead, UserInfoUpdate, TGFromUser, UserInfoReadTG

router = APIRouter()


@router.post("", response_model=UserInfoRead, dependencies=[Depends(current_active_user)])
def create_a_user_info(user: UserInfoCreate, db: Session = Depends(get_session)):
    return create_user_info(user=user, db=db)


@router.get("/not_finished_onboarding", response_model=list[tuple[UserInfoRead, UserRead]],
            dependencies=[Depends(current_superuser)])
def get_users_not_finished_onboarding_route(db: Session = Depends(get_session)):
    return read_users_unfinished_onboarding(db=db)


@router.get("/access_ended", response_model=list[tuple[UserInfoRead, UserRead]],
            dependencies=[Depends(current_superuser)])
def get_users_with_ended_access_route(db: Session = Depends(get_session)):
    return read_users_ended_access(db=db)

@router.get("/for_pushes", response_model=list[UserInfoRead],
            dependencies=[Depends(current_superuser)])
def get_users_for_pushes_route(db: Session = Depends(get_session)):
    return read_users_for_pushes(db=db)


@router.get("/me", response_model=UserInfoRead, dependencies=[Depends(current_active_user)])
def get_my_user_info(db: Session = Depends(get_session), current_user: User = Depends(current_active_user)):
    return read_my_user_info(db=db, current_user=current_user)

@router.patch("/me", response_model=UserInfoRead, dependencies=[Depends(current_active_user)])
def update_a_user(user_info: UserInfoUpdate, user: User = Depends(current_active_user), db: Session = Depends(get_session)):
    return update_my_user_info(user_info=user_info, user=user, db=db)

@router.patch("/update_my_picture", dependencies=[Depends(current_active_user)])
def update_user_picture_router(file: UploadFile = File(...), db: Session = Depends(get_session),
                               user: User = Depends(current_active_user)):
    return update_user_picture(user=user, file=file, db=db)


@router.get("/users_to_rent_in_country/{country}", dependencies=[Depends(current_superuser)],
            response_model=List[UserInfoReadTG])
def get_users_who_want_to_rent_in_a_country_route(country: str, db: Session = Depends(get_session)):
    return get_user_who_want_to_rent_in_a_country(country=country, db=db)

@router.get("/{user_id}", response_model=UserInfoRead, dependencies=[Depends(current_active_user)])
def get_a_user_info(user_id: UUID4, db: Session = Depends(get_session)):
    return read_user_info(user_id=user_id, db=db)

@router.patch("/{user_id}", response_model=UserInfoRead, dependencies=[Depends(current_active_user)])
def update_a_user(user_id: UUID4, user: UserInfoUpdate, db: Session = Depends(get_session)):
    return update_user_info(user_id=user_id, user=user, db=db)


@router.delete("/{user_id}", dependencies=[Depends(current_superuser)])
def delete_a_user(user_id: UUID4, db: Session = Depends(get_session)):
    return delete_user_info(user_id=user_id, db=db)


