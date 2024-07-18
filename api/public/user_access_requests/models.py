from datetime import datetime
from enum import Enum

from pydantic import UUID4
from sqlalchemy import Column
from sqlmodel import Field, SQLModel, Relationship, JSON
from typing import Optional, Dict, Any


class AccessRequestStatus(str, Enum):
    CREATED = 'created'
    PRE_SENT_TO_ADMINS = 'pre_sent_to_admins'
    SENT_TO_ADMINS = 'sent_to_admins'
    INFO_REQUESTED = 'info_requested'
    DECLINED = 'declined'
    ACCEPTED = 'accepted'
    IN_CHAT = 'in_chat'
    NO_PAYSLIP_REPOST = 'no_payslip_repost'
    BAD_REPOST = 'bad_repost'
    def __str__(self) -> str:
        return self.value

class UserAccessRequestBase(SQLModel):
    status: Optional[AccessRequestStatus] = Field(default=AccessRequestStatus.CREATED)


class UserAccessRequest(UserAccessRequestBase, table=True):
    user_id: UUID4 = Field(foreign_key='user.id')
    user_access_request_id: Optional[int] = Field(default=None, primary_key=True)
    admin_messages_tg: Optional[list[dict]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}, )

    class Config:
        arbitrary_types_allowed = True #For JSON to work


class UserAccessRequestCreate(UserAccessRequestBase):
    status: Optional[AccessRequestStatus] = Field(default=AccessRequestStatus.CREATED)
    pass

class UserAccessRequestUpdate(UserAccessRequestBase):
    user_access_request_id: Optional[int] = None
    admin_messages_tg: Optional[list[dict]] = Field(default=None, sa_column=Column(JSON))
    class Config:
        arbitrary_types_allowed = True #For JSON to work
    pass


class UserAccessRequestRead(UserAccessRequestBase):
    user_id: UUID4
    user_access_request_id: int
    admin_messages_tg: Optional[list[dict]] = Field(default=None, sa_column=Column(JSON))
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        arbitrary_types_allowed = True #For JSON to work
    pass
