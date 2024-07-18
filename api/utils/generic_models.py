from pydantic import UUID4
from sqlmodel import Field, SQLModel


# class UserOAuthAccountLink(SQLModel, table=True):
#     user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
#     oauthaccount_id: int | None = Field(default=None, foreign_key="oauthaccount.id", primary_key=True)

class UserListingLink(SQLModel, table=True):
    user_id: UUID4 = Field(default=None, foreign_key="user.id", primary_key=True)
    listing_id: int | None = Field(default=None, foreign_key="listing.listing_id", primary_key=True)


class ListingListingPictureLink(SQLModel, table=True):
    listing_id: int | None = Field(default=None, foreign_key="listing.listing_id", primary_key=True)
    listing_picture_id: int | None = Field(default=None, foreign_key="listingpicture.listing_picture_id", primary_key=True)
