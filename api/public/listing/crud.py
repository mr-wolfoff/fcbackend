from datetime import timedelta, date
from typing import List

from fastapi import Depends, HTTPException, status, UploadFile
from sqlalchemy import desc, func, and_, distinct, tuple_
from sqlmodel import Session, select

from api.auth import current_accepted_user
from api.database import get_session
from api.public.listing.models import Listing, ListingCreate, ListingUpdate, ListingStatus, ListingRead
from api.public.listing_picture.models import ListingPicture, ListingPictureStatus
from api.public.user.models import User
from api.utils.generic_models import ListingListingPictureLink
from backend_services.aws_interaction import upload_file_to_s3_from_api


def create_listing(listing: ListingCreate, db: Session = Depends(get_session),
                   user: User = Depends(current_accepted_user)):
    listing_to_db = Listing(**listing.dict())
    if listing_to_db.user_id is None:
        listing_to_db.user_id = user.id
    db.add(listing_to_db)
    db.commit()
    db.refresh(listing_to_db)
    return listing_to_db

def read_listings(offset: int = 0, limit: int = 3,
                  status: ListingStatus = ListingStatus.POSTED,
                  db: Session = Depends(get_session)):
    listings = db.exec(select(Listing).where(Listing.status == status).order_by(desc(Listing.created_at)).offset(offset).limit(limit)).all()
    return listings


def read_listings_for_preview(offset: int = 0, limit: int = 3,
                  status: ListingStatus = ListingStatus.POSTED,
                  db: Session = Depends(get_session)):
    listings = db.exec(select(Listing).where(and_(Listing.status == status, Listing.is_for_preview)).order_by(desc(Listing.created_at)).offset(offset).limit(limit)).all()
    return listings

def count_active_listings_for_days(days: int = 5, db: Session = Depends(get_session)):
    listing_count, country_count = db.exec(select(func.count(distinct(Listing.listing_id)),
                                                  func.count(distinct(Listing.country)))
                  .where(and_(Listing.status.in_([ListingStatus.POSTED, ListingStatus.UPDATE_POSTED]),
                              Listing.created_at >= date.today() - timedelta(days=days))
                         ) \
                  ).one()
    # print(listing_count, country_count)
    return listing_count, country_count


def add_listing_picture(listing_id: int, file: UploadFile, db: Session = Depends(get_session)):
    file_link = upload_file_to_s3_from_api(file, aws_file_name=f'{listing_id}_{file.filename}')
    listing_picture_to_db = ListingPicture(listing_id=listing_id)
    listing_picture_to_db.picture_url = file_link
    db.add(listing_picture_to_db)
    db.commit()
    db.refresh(listing_picture_to_db)
    link = ListingListingPictureLink(listing_id=listing_picture_to_db.listing_id,
                                     listing_picture_id=listing_picture_to_db.listing_picture_id)
    db.add(link)
    return listing_picture_to_db


def add_listing_pictures(listing_id: int, files: List[UploadFile], db: Session = Depends(get_session)):
    listing_pictures = list()
    for file in files:
        listing_pictures.append(add_listing_picture(listing_id=listing_id, file=file, db=db))
    return listing_pictures


def add_listing_pictures_from_another_listing(listing_id: int, from_listing_id: int, db: Session = Depends(get_session)):
    listing_pictures = db.exec(select(ListingPicture).where(ListingPicture.listing_id == from_listing_id,
                                                        ListingPicture.status == ListingPictureStatus.USED)).all()
    print(listing_pictures)
    for listing_picture in listing_pictures:
        listing_picture_to_db = ListingPicture(listing_id=listing_id,
                                               picture_url=listing_picture.picture_url)
        db.add(listing_picture_to_db)
        db.commit()
        db.refresh(listing_picture_to_db)
        link = ListingListingPictureLink(listing_id=listing_picture_to_db.listing_id,
                                         listing_picture_id=listing_picture_to_db.listing_picture_id)
        db.add(link)
    db.commit()
    listing = db.get(Listing, listing_id)
    return listing


def set_new_listing_pictures(listing_id: int, files: List[UploadFile], db: Session = Depends(get_session)):
    set_old_listing_pictures_as_inactive(listing_id=listing_id, db=db)
    listing_pictures = add_listing_pictures(listing_id=listing_id, files=files, db=db)
    return listing_pictures


def set_old_listing_pictures_as_inactive(listing_id: int, db: Session = Depends(get_session)):
    listing = db.get(Listing, listing_id)
    listing_pictures = listing.listing_pictures
    for lp in listing_pictures:
        lp.status = ListingPictureStatus.DELETED
    db.commit()



def read_listing(listing_id: int, db: Session = Depends(get_session)):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing not found with id: {listing_id}",
        )
    return listing


def read_listing_by_statuses(statuses: list[ListingStatus], db: Session = Depends(get_session)):
    statement = select(Listing).where(Listing.status.in_(statuses))
    listings = db.exec(statement).all()
    return listings



def read_my_listing(listing_id: int, db: Session, user: User):
    listing = db.get(Listing, listing_id)
    if listing.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can not get other person listing: {listing_id}",
        )
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing not found with id: {listing_id}",
        )
    return listing



def read_listings_of_user_id(user_id: int, db: Session = Depends(get_session)) -> [Listing]:
    listings = db.exec(select(Listing).where(Listing.user_id == user_id).order_by(desc(Listing.created_at))).all()
    return listings

def read_listings_of_user(user: User, db: Session = Depends(get_session), limit: int = 5,
                          posted_only: bool = False) -> [Listing]:
    if posted_only:
        listings = db.exec(
            select(Listing).where(Listing.user_id == user.id,
                                  Listing.status.in_([ListingStatus.POSTED, ListingStatus.UPDATE_POSTED]))\
                .order_by(desc(Listing.created_at)).limit(limit)).all()
    else:
        listings = db.exec(select(Listing).where(Listing.user_id == user.id,
                                                 Listing.country.isnot(None)).order_by(desc(Listing.created_at)).limit(limit)).all()
    return listings

def update_listing(listing_id: int, listing: ListingUpdate, db: Session,
                   user: User | None = None):
    listing_to_update = db.get(Listing, listing_id)
    if user is not None:
        if user.id != listing_to_update.user_id:
            if not listing_to_update:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You cannot update not your listing: {listing_id}",
                )
    if not listing_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing not found with id: {listing_id}",
        )
    listing_data = listing.dict(exclude_unset=True)
    for key, value in listing_data.items():
        setattr(listing_to_update, key, value)
    db.add(listing_to_update)
    db.commit()
    db.refresh(listing_to_update)
    return listing_to_update

def delete_listing(listing_id: int, db: Session = Depends(get_session),
                   current_user: User = Depends(current_accepted_user)):
    listing = db.get(Listing, listing_id)
    if not listing.user_id == current_user.id or not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"You cannot delete other users listings! listing_id: {listing_id}",
        )
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing not found with id: {listing_id}",
        )
    db.delete(listing)
    db.commit()
    return {"ok": True}