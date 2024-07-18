from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.auth import current_accepted_user, current_active_user, current_superuser
from api.database import get_session
from api.public.user.models import User
from api.public.user_access_requests.crud import create_user_access_request, update_user_access_request, \
    get_user_access_request, get_user_access_requests_by_statuses_days, get_last_user_access_request
from api.public.user_access_requests.models import UserAccessRequestCreate, UserAccessRequestRead, \
    UserAccessRequestUpdate, AccessRequestStatus

router = APIRouter()

@router.post("", dependencies=[Depends(current_active_user)], response_model=UserAccessRequestRead)
def create_access_request_route(user_access_request: UserAccessRequestCreate, db: Session = Depends(get_session),
                                user: User = Depends(current_active_user)):
    return create_user_access_request(user_access_request=user_access_request, db=db, user=user)


@router.post("/by_statuses", dependencies=[Depends(current_superuser)], response_model=list[UserAccessRequestRead])
def get_access_requests_by_statuses_route(statuses: list[AccessRequestStatus], days: int, db: Session = Depends(get_session)):
    return get_user_access_requests_by_statuses_days(statuses=statuses, days=days, db=db)

@router.get("/me/last", dependencies=[Depends(current_active_user)], response_model=UserAccessRequestRead)
def get_my_last_access_request_route(db: Session = Depends(get_session), user: User = Depends(current_active_user)):
    return get_last_user_access_request(db=db, user=user)


@router.patch("/{request_id}", dependencies=[Depends(current_active_user)], response_model=UserAccessRequestRead)
def update_access_request_route(request_id: int, user_access_request: UserAccessRequestUpdate,
                                db: Session = Depends(get_session)):
    return update_user_access_request(request_id=request_id, user_access_request=user_access_request, db=db)


@router.get("/{request_id}", dependencies=[Depends(current_active_user)], response_model=UserAccessRequestRead)
def get_access_request_route(request_id: int, db: Session = Depends(get_session)):
    return get_user_access_request(request_id=request_id, db=db)