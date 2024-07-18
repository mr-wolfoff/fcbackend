from datetime import datetime
from typing import Optional
import uuid

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid


class Review(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=uuid.uuid4, primary_key=True)
    user_id_from: uuid.UUID = Field(foreign_key="user.id")
    user_id_to: uuid.UUID = Field(foreign_key="user.id")
    rating: str
    review_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    from_user: Optional["User"] = Relationship(back_populates="reviews_from")
    to_user: Optional["User"] = Relationship(back_populates="reviews_to")

    class Config:
        orm_mode = True


class ReviewCreate(SQLModel):
    user_id_from: uuid.UUID
    user_id_to: uuid.UUID
    rating: str
    review_text: Optional[str] = None


class ReviewUpdate(SQLModel):
    rating: Optional[str]
    review_text: Optional[str]


class ReviewRead(SQLModel):
    id: uuid.UUID
    user_id_from: uuid.UUID
    user_id_to: uuid.UUID
    rating: str
    review_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
