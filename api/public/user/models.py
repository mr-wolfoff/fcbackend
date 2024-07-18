# from dataclasses import dataclass
# from typing import Optional, List
#
# from sqlalchemy.orm import relationship, Mapped
from datetime import datetime
from typing import Optional

from pydantic import UUID4
from sqlalchemy.orm import relationship
from sqlmodel import Field, SQLModel, Relationship
# from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase, SQLAlchemyBaseOAuthAccountTableUUID
from fastapi_users_db_sqlmodel import SQLModelBaseOAuthAccount, SQLModelBaseUserDB

import uuid

from fastapi_users import schemas

from api.utils.generic_models import UserListingLink

TYPE_CHECKING = True



class OAuthAccount(SQLModelBaseOAuthAccount, table=True):
    user: "User" = Relationship(back_populates="oauth_accounts")
    pass


class User(SQLModelBaseUserDB, table=True):

    email: str = Field(
        sa_column_kwargs={"unique": True, "index": True}, nullable=False
    )
    is_accepted: bool = Field(False, nullable=False)
    oauth_accounts: list[OAuthAccount] = Relationship(back_populates='user')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},)
    premium_until: Optional[datetime] = Field(default=None)
    info: "UserInfo" = Relationship(sa_relationship=relationship("UserInfo", cascade="all, delete", back_populates="user"))
    listings: list["Listing"] = Relationship(back_populates="user", link_model=UserListingLink)





class UserRead(schemas.BaseUser[uuid.UUID]):
    is_accepted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    premium_until: Optional[datetime] = Field(default=None)
    pass

class UserReadAdmin(schemas.BaseUser[uuid.UUID]):
    is_accepted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    premium_until: Optional[datetime] = Field(default=None)
    pass


class UserCreate(schemas.BaseUserCreate):
    is_accepted: bool = Field(False, nullable=False)
    pass


class UserUpdate(schemas.BaseUserUpdate):
    is_accepted: Optional[bool] = None
    premium_until: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    id: Optional[UUID4] = Field(default=None)
    pass

class UserUpdateAdmin(schemas.BaseUserUpdate):
    is_accepted: Optional[bool] = None
    premium_until: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    id: Optional[UUID4] = Field(default=None)
    pass

