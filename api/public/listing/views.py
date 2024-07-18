from typing import List

from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlmodel import Session

from api.auth import current_accepted_user, current_superuser, current_superuser_or_accepted_user, current_active_user
from api.database import get_session
from api.public.listing.crud import (
    create_listing,
    delete_listing,
    read_listing,
    read_listings,
    update_listing, read_listings_of_user, read_listings_of_user_id, add_listing_picture, add_listing_pictures,
    set_new_listing_pictures, read_my_listing, read_listing_by_statuses, read_listings_for_preview,
    count_active_listings_for_days, add_listing_pictures_from_another_listing,
)
from api.public.listing.models import ListingCreate, ListingRead, ListingUpdate, ListingStatus
from api.public.listing_picture.models import ListingPictureRead
from api.public.user.models import User

router = APIRouter()


@router.post("", response_model=ListingRead, dependencies=[Depends(current_accepted_user)])
def create_a_listing(listing: ListingCreate, db: Session = Depends(get_session),
                     user: User = Depends(current_accepted_user)):
    return create_listing(listing=listing, db=db, user=user)

@router.get("", response_model=list[ListingRead], dependencies=[Depends(current_accepted_user)])
def get_listings(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    status: ListingStatus = ListingStatus.POSTED,
    db: Session = Depends(get_session),
):
    return read_listings(offset=offset, limit=limit, status=status, db=db)


@router.get("/for_preview/count", dependencies=[Depends(current_active_user)])
def count_listings_for_preview_route(
        days: int, db: Session = Depends(get_session),
):
    listing_count, country_count = count_active_listings_for_days(days=days, db=db)
    return {'listing_count': listing_count, 'country_count': country_count}

@router.get("/for_preview", response_model=list[ListingRead], dependencies=[Depends(current_active_user)],
            response_model_exclude={"user_id", "user"})
def get_listings(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    status: ListingStatus = ListingStatus.POSTED,
    db: Session = Depends(get_session),
):
    return read_listings_for_preview(offset=offset, limit=limit, status=status, db=db)

@router.get("/user/me", response_model=list[ListingRead], dependencies=[Depends(current_accepted_user)])
def get_listings_of_me(
    user: User = Depends(current_accepted_user),
    db: Session = Depends(get_session),
    limit: int = 5,
    posted_only: bool = False,
):
    return read_listings_of_user(user=user, db=db, limit=limit, posted_only=posted_only)

@router.get("/user/{user_id}", response_model=list[ListingRead], dependencies=[Depends(current_accepted_user)])
def get_listings_of_user(
    user_id: int,
    db: Session = Depends(get_session),
):
    return read_listings_of_user_id(user_id=user_id, db=db)

@router.get("/me/{listing_id}", response_model=ListingRead, dependencies=[Depends(current_accepted_user)])
def get_my_listing(listing_id: int, db: Session = Depends(get_session), user: User = Depends(current_accepted_user)):
    return read_my_listing(listing_id=listing_id, db=db, user=user)

@router.patch("/me/{listing_id}", response_model=ListingRead, dependencies=[Depends(current_accepted_user)])
def update_my_listing_listing(listing_id: int, listing: ListingUpdate, db: Session = Depends(get_session),
                              user: User = Depends(current_accepted_user)):
    return update_listing(listing_id=listing_id, listing=listing, db=db, user=user)


@router.get("/{listing_id}", response_model=ListingRead, dependencies=[Depends(current_superuser_or_accepted_user)])
def get_a_listing(listing_id: int, db: Session = Depends(get_session)):
    return read_listing(listing_id=listing_id, db=db)

@router.post("/statuses", response_model=list[ListingRead], dependencies=[Depends(current_superuser)])
def listing_by_statuses_route(statuses: list[ListingStatus], db: Session = Depends(get_session)):
    return read_listing_by_statuses(statuses=statuses, db=db)


@router.post("/{listing_id}/pictures/from_listing_id={from_listing_id}", response_model=ListingRead,
             dependencies=[Depends(current_accepted_user)])
def add_pictures_to_listing_from_another_route(listing_id: int, from_listing_id: int, db: Session = Depends(get_session),
                            user: User = Depends(current_accepted_user)):
    return add_listing_pictures_from_another_listing(listing_id=listing_id, from_listing_id=from_listing_id, db=db)


@router.post("/{listing_id}/pictures", response_model=List[ListingPictureRead],
             dependencies=[Depends(current_accepted_user)])
def add_pictures_to_listing(listing_id: int, files: List[UploadFile] = File(...), db: Session = Depends(get_session)):
    return add_listing_pictures(listing_id=listing_id, files=files, db=db)

@router.post("/{listing_id}/picture", response_model=ListingPictureRead, dependencies=[Depends(current_accepted_user)])
def add_picture_to_listing(listing_id: int, file: UploadFile = File(...), db: Session = Depends(get_session)):
    return add_listing_picture(listing_id=listing_id, file=file, db=db)


@router.post("/{listing_id}/new_pictures", response_model=List[ListingPictureRead], dependencies=[Depends(current_accepted_user)])
def new_pictures_to_listing(listing_id: int, files: List[UploadFile] = File(...), db: Session = Depends(get_session)):
    return set_new_listing_pictures(listing_id=listing_id, files=files, db=db)


@router.patch("/{listing_id}", response_model=ListingRead, dependencies=[Depends(current_superuser)])
def update_a_listing(listing_id: int, listing: ListingUpdate, db: Session = Depends(get_session)):
    return update_listing(listing_id=listing_id, listing=listing, db=db)

@router.delete("/{listing_id}", dependencies=[Depends(current_accepted_user)])
def delete_a_listing(listing_id: int, db: Session = Depends(get_session),
                     current_user: User = Depends(current_accepted_user)):
    return delete_listing(listing_id=listing_id, db=db, current_user=current_user)