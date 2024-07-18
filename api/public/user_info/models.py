from dataclasses import dataclass
from typing import Optional

from pydantic import UUID4
from sqlalchemy import Column, BigInteger
from sqlalchemy.orm import relationship
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime


class UserInfoBase(SQLModel):
    full_name: Optional[str] = Field(default=None)
    how_did_you_hear: Optional[str] = None
    tg_id: Optional[int] = Field(default=None, sa_column=Column(BigInteger()))
    onboarding_step: Optional[float] = Field(default=None)
    onboarding_completed: Optional[bool] = Field(default=False)
    tg_username: Optional[str] = Field(default=None)
    whatsapp: Optional[str] = Field(default=None)
    instagram: Optional[str] = Field(default=None)
    linkedin: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    picture_url: Optional[str] = Field(default=None)
    where_to_rent: Optional[str] = Field(default=None)
    where_to_let: Optional[str] = Field(default=None)
    meet: Optional[bool] = Field(default=None)
    notifications: Optional[bool] = Field(default=True)
    contact_email: Optional[str] = Field(default=None)
    blocked_timestamp: Optional[datetime] = Field(default=None)
    bot_name: Optional[str] = Field(default=None)
    pass

class UserInfo(UserInfoBase, table=True):
    user_id: UUID4 = Field(default=None, primary_key=True, foreign_key='user.id')
    user: "User" = Relationship(sa_relationship=relationship("User", back_populates="info"))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}, )

    @dataclass
    class Config:
        from_attributes = True


class UserInfoCreate(UserInfoBase):
    pass

class UserInfoRead(UserInfoBase):
    user_id: UUID4
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserInfoReadTG(SQLModel):
    user_id: UUID4
    tg_id: Optional[int] = Field(None, sa_column=Column(BigInteger()))


class UserInfoUpdate(UserInfoBase):
    user_id: Optional[UUID4] = None
    pass


class TGFromUser(SQLModel):
    id: Optional[int]
    is_bot: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
