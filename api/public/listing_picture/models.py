from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from api.utils.generic_models import ListingListingPictureLink

class ListingPictureStatus(str, Enum):
    USED = "used"
    DELETED = "deleted"
    def __str__(self) -> str:
        return self.value

class ListingPictureBase(SQLModel):
    status: Optional[ListingPictureStatus] = Field(default=ListingPictureStatus.USED)
    listing_id: int = Field(foreign_key='listing.listing_id')


class ListingPicture(ListingPictureBase, table=True):
    listing_picture_id: Optional[int] = Field(default=None, primary_key=True)
    picture_url: Optional[str]
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}, )
    listing: "Listing" = Relationship(back_populates="listing_pictures", link_model=ListingListingPictureLink)

class ListingPictureCreate(ListingPictureBase):
    pass

class ListingPictureRead(ListingPictureBase):
    listing_picture_id: int
    listing_id: int
    picture_url: str
    status: ListingPictureStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ListingPictureUpdate(ListingPictureBase):
    picture_url: Optional[str] = None
    status: Optional[ListingPictureStatus] = None
