from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.auth import local_fastapi_users, auth_backend, google_oauth_client, SECRET, current_active_user, \
    current_superuser
from api.database import get_session
from api.public.user.crud import read_user_by_email, reset_user
# from api.database import get_session
# from api.public.user.crud import (
#     create_user,
#     delete_user,
#     read_user,
#     read_users,
#     update_user,
# )
from api.public.user.models import UserCreate, UserRead, UserUpdate, User, UserUpdateAdmin, UserReadAdmin

router = APIRouter()

auth_router = local_fastapi_users.get_auth_router(auth_backend)
register_router = local_fastapi_users.get_register_router(UserRead, UserCreate)
reset_password_router = local_fastapi_users.get_reset_password_router()
verify_router = local_fastapi_users.get_verify_router(UserRead)
users_router = local_fastapi_users.get_users_router(UserRead, UserUpdate)
users_admin_router = local_fastapi_users.get_users_router(UserReadAdmin, UserUpdateAdmin)
oauth_router = local_fastapi_users.get_oauth_router(google_oauth_client, auth_backend, SECRET, associate_by_email=True,
                                                    is_verified_by_default=True)
oauth_associate_router = local_fastapi_users.get_oauth_associate_router(google_oauth_client, UserRead, "SECRET")



@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@router.get("/email/{email}", dependencies=[Depends(current_superuser)])
async def email_route(email: str, db: Session = Depends(get_session)):
    return read_user_by_email(email=email, db=db)

@router.get("/me/reset", dependencies=[Depends(current_active_user)], response_model=UserRead)
async def reset_me_route(db: Session = Depends(get_session), user: User = Depends(current_active_user)):
    return reset_user(db=db, user=user)


# @router.post("", response_model=UserRead)
# def create_a_user(user: UserCreate, db: Session = Depends(get_session)):
#     return create_user(user=user, db=db)
#
#
# @router.get("", response_model=list[UserRead])
# def get_users(
#     offset: int = 0,
#     limit: int = Query(default=100, lte=100),
#     db: Session = Depends(get_session),
# ):
#     return read_users(offset=offset, limit=limit, db=db)
#
# @router.get("/{user_id}", response_model=UserRead)
# def get_a_user(user_id: int, db: Session = Depends(get_session)):
#     return read_user(user_id=user_id, db=db)
#
#
# @router.patch("/{user_id}", response_model=UserRead)
# def update_a_user(user_id: int, user: UserUpdate, db: Session = Depends(get_session)):
#     return update_user(user_id=user_id, user=user, db=db)
#
#
# @router.delete("/{user_id}")
# def delete_a_user(user_id: int, db: Session = Depends(get_session)):
#     return delete_user(user_id=user_id, db=db)
