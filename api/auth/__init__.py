import json
import os
import uuid
from typing import Optional

from fastapi import Depends, Request, APIRouter, status, HTTPException
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
# from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlmodel import SQLModelUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from sqlmodel import Session

from api.public.user.models import User, UserRead, UserCreate, UserUpdate, OAuthAccount
from api.database import get_session

from dotenv import load_dotenv
load_dotenv()

SECRET = "SECRET"
try:
    with open(os.getenv('GOOGLE_AUTH_JSON_PATH', "")) as json_file:
        credentials = json.load(json_file)
        google_oauth_client = GoogleOAuth2(
            credentials.get('web').get('client_id'),
            credentials.get('web').get('client_secret'),
        )
except:
    google_oauth_client = GoogleOAuth2('client_id', 'client_secret')
    pass




class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


def get_user_db(session: Session = Depends(get_session)):
    yield SQLModelUserDatabase(session, User, OAuthAccount)

def get_user_manager(user_db: SQLModelUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=60*60*24*30*3)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

local_fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = local_fastapi_users.current_user(active=True)


def current_accepted_user(user: User = Depends(current_active_user)):
    if not user.is_accepted and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not accepted yet",
        )
    return user


def current_superuser(user: User = Depends(current_active_user)):
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not superuser",
        )
    return user

def current_superuser_or_accepted_user(user: User = Depends(current_active_user)):
    if not user.is_accepted and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not accepted or superuser",
        )
