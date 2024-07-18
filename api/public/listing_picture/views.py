import json
from typing import List

from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlmodel import Session

from api.auth import current_accepted_user
from api.database import get_session
from api.public.listing_picture.crud import (
    create_listing_picture,
    delete_listing_picture,
    read_listing_picture,
    read_listing_pictures,
    update_listing_picture, read_listing_pictures_by_listing, create_listing_pictures,
)
from api.public.listing_picture.models import ListingPictureCreate, ListingPictureRead, ListingPictureUpdate, \
    ListingPicture, ListingPictureBase
from api.public.user.models import User

router = APIRouter()

@router.post("", response_model=ListingPictureRead, dependencies=[Depends(current_accepted_user)])
def upload_listing_picture_router(listing_picture: ListingPictureCreate = Depends(), file: UploadFile = File(...),
                                  db: Session = Depends(get_session)):
    return create_listing_picture(listing_picture=listing_picture, file=file, db=db)

@router.post("/upload", response_model=List[ListingPictureRead], dependencies=[Depends(current_accepted_user)])
def upload_listing_pictures_router(listing_picture: ListingPictureBase = Depends(), files: List[UploadFile] = File(...),
                                   db: Session = Depends(get_session)):
    return create_listing_pictures(listing_picture=listing_picture, files=files, db=db)

@router.get("/listing/{listing_id}", response_model=list[ListingPictureRead],
            dependencies=[Depends(current_accepted_user)])
def get_listing_pictures_by_listing(
    listing_id: int,
    db: Session = Depends(get_session),
):
    return read_listing_pictures_by_listing(listing_id=listing_id, db=db)

@router.patch("/{listing_picture_id}", response_model=ListingPictureRead,
              dependencies=[Depends(current_accepted_user)])
def update_a_listing_picture(listing_picture_id: int, listing_picture: ListingPictureUpdate, db: Session = Depends(get_session)):
    return update_listing_picture(listing_picture_id=listing_picture_id, listing_picture=listing_picture, db=db)

@router.delete("/{listing_picture_id}", dependencies=[Depends(current_accepted_user)])
def delete_a_listing_picture(listing_picture_id: int, db: Session = Depends(get_session),
                             current_user: User = Depends(current_accepted_user)):
    return delete_listing_picture(listing_picture_id=listing_picture_id, db=db, current_user=current_user)

