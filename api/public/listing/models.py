from enum import Enum

from pydantic import UUID4
from sqlalchemy import Column, BigInteger
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from api.public.listing_picture.models import ListingPicture, ListingPictureRead, ListingPictureStatus
from api.utils.generic_models import UserListingLink, ListingListingPictureLink
from typing import Any, Optional

class ListingStatus(str, Enum):
    CREATED = "created"
    FINISHED = "finished"
    SENT_TO_ADMINS = "sent_to_admins"
    UPDATE_SENT_TO_ADMINS = "update_sent_to_admins"
    POSTED = "posted"
    UPDATED = "updated"
    UPDATE_POSTED = "update_posted"
    DUMPED = "dumped"
    INFO_NEEDED = "info_needed"
    PAYMENT_NEEDED = "payment_needed"
    ACTIVE = 'active'

    def __str__(self) -> str:
        return self.value


class ListingBase(SQLModel):
    description: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    price: Optional[str] = None
    comments: Optional[str] = None
    is_rented: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_ids: Optional[str] = Field(default=None)
    channel_id: Optional[int] = Field(default=None, sa_column=Column(BigInteger()))
    status: Optional[ListingStatus] = Field(default=ListingStatus.CREATED)

class Listing(ListingBase, table=True):
    listing_id: int | None = Field(primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}, )
    user_id: UUID4 = Field(foreign_key='user.id')
    user: "User" = Relationship(back_populates="listings", link_model=UserListingLink)  # type: ignore
    listing_pictures: list[ListingPicture] = Relationship(back_populates="listing", link_model=ListingListingPictureLink)
    is_for_preview: Optional[bool] = Field(default=None)

    @property
    def used_listing_pictures(self) -> list[ListingPicture]:
        return sorted([picture for picture in self.listing_pictures if picture.status == ListingPictureStatus.USED],
                      key=lambda picture: picture.listing_picture_id)


class ListingCreate(ListingBase):
    pass


class ListingRead(ListingBase):
    listing_id: int
    user_id: UUID4 = Field(foreign_key='user.id')
    user: "UserRead" = Relationship(back_populates="listings", link_model=UserListingLink)
    # listing_pictures: list[ListingPictureRead] | None = None
    used_listing_pictures: list[ListingPictureRead] | None = None


class ListingPreview(ListingBase):
    listing_id: int
    # listing_pictures: list[ListingPictureRead] | None = None
    used_listing_pictures: list[ListingPictureRead] | None = None



class ListingUpdate(ListingBase):
    listing_id: int
