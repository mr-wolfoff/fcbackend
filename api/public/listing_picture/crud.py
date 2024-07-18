from fastapi import Depends, HTTPException, status, UploadFile
from sqlmodel import Session, select

from api.auth import current_active_user
from api.database import get_session
from api.public.listing_picture.models import ListingPicture, ListingPictureCreate, ListingPictureUpdate, \
    ListingPictureBase, ListingPictureStatus
from api.public.user.models import User
from api.utils.generic_models import ListingListingPictureLink
from backend_services.aws_interaction import upload_file_to_s3_from_api


def create_listing_picture(listing_picture: ListingPictureCreate, file: UploadFile,
                           db: Session = Depends(get_session)) -> ListingPicture:
    file_link = upload_file_to_s3_from_api(file, aws_file_name=f'{listing_picture.listing_id}_{file.filename}')
    listing_picture_to_db = ListingPicture(**listing_picture.dict())
    listing_picture_to_db.picture_url = file_link
    db.add(listing_picture_to_db)
    db.commit()
    db.refresh(listing_picture_to_db)
    link = ListingListingPictureLink(listing_id=listing_picture_to_db.listing_id,
                                     listing_picture_id=listing_picture_to_db.listing_picture_id)
    db.add(link)
    db.commit()
    return listing_picture_to_db


def create_listing_pictures(listing_picture: ListingPictureBase, files: list[UploadFile],
                            db: Session = Depends(get_session)) -> list[ListingPicture]:
    listing_pictures = list()
    for file in files:
        listing_pictures.append(create_listing_picture(listing_picture=listing_picture, file=file, db=db))

    return listing_pictures

def read_listing_pictures(offset: int = 0, limit: int = 20, db: Session = Depends(get_session)):
    listing_pictures = db.exec(select(ListingPicture).where(ListingPicture.status != ListingPictureStatus.DELETED)\
                               .offset(offset).limit(limit)).all()
    return listing_pictures


def read_listing_picture(listing_picture_id: int, db: Session = Depends(get_session)):
    listing_picture = db.get(ListingPicture, listing_picture_id)
    if not listing_picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing picture not found with id: {listing_picture_id}",
        )
    return listing_picture


def read_listing_pictures_by_listing(listing_id: int, db: Session = Depends(get_session)):
    listing_pictures = db.exec(select(ListingPicture).where(ListingPicture.listing_id == listing_id)\
                               .where(ListingPicture.status != ListingPictureStatus.DELETED)).all()
    return listing_pictures

def update_listing_picture(listing_picture_id: int, listing_picture: ListingPictureUpdate, db: Session = Depends(get_session)):
    listing_picture_to_update = db.get(ListingPicture, listing_picture_id)
    if not listing_picture_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing picture not found with id: {listing_picture_id}",
        )

    listing_picture_data = listing_picture.dict(exclude_unset=True)
    for key, value in listing_picture_data.items():
        setattr(listing_picture_to_update, key, value)

    db.add(listing_picture_to_update)
    db.commit()
    db.refresh(listing_picture_to_update)
    return listing_picture_to_update

def delete_listing_picture(listing_picture_id: int, db: Session = Depends(get_session),
                           current_user: User = Depends(current_active_user)):
    listing_picture = db.get(ListingPicture, listing_picture_id)
    if not listing_picture.listing.user_id == current_user.id or not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You cannot delete other users' listing picture. {listing_picture_id}",
        )
    if not listing_picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing picture not found with id: {listing_picture_id}",
        )
    listing_picture.status = ListingPictureStatus.DELETED
    db.add(listing_picture)
    db.commit()
    return {"ok": True}

def restore_listing_picture(listing_picture_id: int, db: Session = Depends(get_session)):
    listing_picture = db.get(ListingPicture, listing_picture_id)
    if not listing_picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing picture not found with id: {listing_picture_id}",
        )
    listing_picture.status = ListingPictureStatus.USED
    db.add(listing_picture)
    db.commit()
    db.refresh(listing_picture)
    return listing_picture