from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, UploadFile
from sqlmodel import Session, select

from api.auth import current_active_user
from api.database import get_session
from api.public.user.models import User
from api.public.user_access_requests.models import UserAccessRequestCreate, UserAccessRequestRead, UserAccessRequest, \
    UserAccessRequestUpdate, AccessRequestStatus
from api.utils.generic_functions import set_model_from_another_model


def create_user_access_request(user_access_request: UserAccessRequestCreate, db: Session = Depends(get_session),
                               user: User = Depends(current_active_user)) -> UserAccessRequest:
    user_access_request_to_db = UserAccessRequest(user_id=user.id, status=user_access_request.status,)
    db.add(user_access_request_to_db)
    db.commit()
    db.refresh(user_access_request_to_db)
    return user_access_request_to_db

def update_user_access_request(request_id: int, user_access_request: UserAccessRequestUpdate,
                               db: Session = Depends(get_session)):
    user_access_request_to_update = db.get(UserAccessRequest, request_id)
    if not user_access_request_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"access request not found with id: {request_id}",
        )

    user_access_request_to_update = set_model_from_another_model(from_model=user_access_request,
                                                                 to_model=user_access_request_to_update)
    db.commit()
    db.refresh(user_access_request_to_update)
    return user_access_request_to_update


def get_user_access_request(request_id: int, db: Session = Depends(get_session)):
    user_access_request = db.get(UserAccessRequest, request_id)
    if not user_access_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"access request not found with id: {request_id}",
        )
    return user_access_request

def get_last_user_access_request(db: Session = Depends(get_session), user: User = Depends(current_active_user)):
    statement = select(UserAccessRequest).where(UserAccessRequest.user_id == user.id)\
        .order_by(UserAccessRequest.created_at.desc())
    access_request = db.exec(statement).first()
    if not access_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"access request not found for user: {user.id}",
        )
    return access_request



def get_user_access_requests_by_statuses_days(statuses: list[AccessRequestStatus], days: int,
                                              db: Session = Depends(get_session)):
    statement = select(UserAccessRequest).where(UserAccessRequest.status.in_(statuses),
                                                UserAccessRequest.updated_at >= datetime.utcnow() - timedelta(days=days))
    access_requests = db.exec(statement).all()
    return access_requests




