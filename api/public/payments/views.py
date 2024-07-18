from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.auth import current_accepted_user, current_active_user, current_superuser
from api.database import get_session
from api.public.user.models import User

from api.public.payments.crud import *
from api.public.payments.models import *

router = APIRouter()

@router.get("/charges/to_collect", dependencies=[Depends(current_superuser)],
            response_model=list[RecursivePaymentChargeRead])
def get_charges_to_collect_route(db: Session = Depends(get_session)):
    result = get_needed_to_run_payment_charges(db=db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No charges found",
        )
    return result

@router.get("/charges/me", dependencies=[Depends(current_active_user)],
            response_model=list[RecursivePaymentChargeRead])
def get_my_payment_charges_route(db: Session = Depends(get_session), user: User = Depends(current_active_user)):
    result = get_my_payment_charges(db=db, user=user)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No charges found",
        )
    return result

@router.get("/charges/me/set_inactive", dependencies=[Depends(current_active_user)],
            response_model=list[RecursivePaymentChargeRead])
def set_my_payment_charges_inactive_route(db: Session = Depends(get_session), user: User = Depends(current_active_user)):
    result = set_my_payment_charges_inactive(db=db, user=user)
    return result

@router.get("/charges/{user_id}/set_inactive", dependencies=[Depends(current_superuser)],
            response_model=list[RecursivePaymentChargeRead])
def set_my_payment_charges_inactive_route(user_id: UUID4, db: Session = Depends(get_session)):
    result = set_payment_charges_of_user_inactive(db=db, user_id=user_id)
    return result

@router.get("/charges/{charge_id}", dependencies=[Depends(current_superuser)],
            response_model=RecursivePaymentChargeRead)
def get_charge_by_id_route(charge_id: int, db: Session = Depends(get_session)):
    result = get_recursive_payment_charge(recursive_payment_charge_id=charge_id, db=db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No charge found with id {id}".format(id=charge_id),
        )
    return result


@router.post("/charges", dependencies=[Depends(current_superuser)],
            response_model=RecursivePaymentChargeRead)
def create_charge_route(charge: RecursivePaymentChargeCreate, db: Session = Depends(get_session)):
    result = create_recursive_payment_charge(charge=charge, db=db)
    return result

@router.patch("/charges", dependencies=[Depends(current_superuser)],
            response_model=RecursivePaymentChargeRead)
def update_charge_route(charge: RecursivePaymentChargeUpdate, db: Session = Depends(get_session)):
    result = update_recursive_payment_charge(charge=charge, db=db)
    return result


@router.get("/me/{days}", dependencies=[Depends(current_active_user)],
            response_model=list[PaymentRead])
def get_my_payments_route(days: int | None, db: Session = Depends(get_session), user: User = Depends(current_active_user)):
    result = get_my_payments_days(days=days, db=db, user=user)
    return result

@router.get("/user/{user_id}/{days}", dependencies=[Depends(current_superuser)],
            response_model=list[PaymentRead])
def get_payments_by_user_days_route(user_id: UUID4, days: int, db: Session = Depends(get_session)):
    result = get_payments_by_user_and_days_before(user_id=user_id, days=days, db=db)
    return result

@router.get("/successful/days={days}&payment_system={payment_system}/", dependencies=[Depends(current_superuser)],
            response_model=list[PaymentRead])
def get_payments_by_user_days_route(days: int, payment_system: str, db: Session = Depends(get_session)):
    result = get_payments_by_days_and_payment_system(days=days, payment_system=payment_system, db=db)
    return result


@router.get("/{payment_id}", dependencies=[Depends(current_superuser)],
            response_model=PaymentRead)
def get_payment_by_id_route(payment_id: int, db: Session = Depends(get_session)):
    result = get_payment(payment_id=payment_id, db=db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payment found with id {id}".format(id=payment_id),
        )
    return result



@router.post("", dependencies=[Depends(current_superuser)],
            response_model=PaymentRead)
def create_payment_route(payment: PaymentCreate, db: Session = Depends(get_session)):
    result = create_payment(payment=payment, db=db)
    return result

@router.patch("", dependencies=[Depends(current_superuser)],
            response_model=PaymentRead)
def update_payment_route(payment: PaymentUpdate, db: Session = Depends(get_session)):
    result = update_payment(payment=payment, db=db)
    return result