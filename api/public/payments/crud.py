from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, status, UploadFile
from pydantic import UUID4
from sqlmodel import Session, select, update

from api.auth import current_active_user
from api.database import get_session
from api.public.user.models import User
from api.public.payments.models import PaymentRead, PaymentUpdate, PaymentCreate, \
    RecursivePaymentChargeUpdate, RecursivePaymentChargeCreate, RecursivePaymentChargeRead, Payment, \
    RecursivePaymentCharge
from sqlalchemy import desc

from api.utils.generic_functions import set_model_from_another_model


def get_payment(payment_id: int, db: Session = Depends(get_session)) -> Payment | None:
    payment = db.get(Payment, payment_id)
    return payment

def get_payments_by_user_and_days_before(user_id: UUID4, days: int, db: Session = Depends(get_session)):
    statement = select(Payment).where(Payment.user_id == user_id,
                                      Payment.created_at >= datetime.utcnow() - timedelta(days=days))
    payments = db.exec(statement).all()
    return payments

def get_payments_by_days_and_payment_system(days: int, payment_system: str, db: Session = Depends(get_session)):
    if payment_system.lower() == 'any':
        statement = select(Payment).where(Payment.status == 'complete',
                                          Payment.created_at >= datetime.utcnow() - timedelta(days=days)
                                          )
    else:
        statement = select(Payment).where(Payment.status == 'complete',
                                          Payment.created_at >= datetime.utcnow() - timedelta(days=days),
                                          Payment.payment_system == payment_system)
    payments = db.exec(statement).all()
    return payments


def get_my_payments_days(days: int | None, db: Session = Depends(get_session), user: User = Depends(current_active_user)) -> (
        list[Payment] | None):
    statement = select(Payment).where(Payment.user_id == user.id, )
    if days:
        statement = statement.where(Payment.created_at >= datetime.utcnow() - timedelta(days=days))
    payments = db.exec(statement).all()
    return payments


def create_payment(payment: PaymentCreate, db: Session = Depends(get_session)) -> Payment | None:
    payment_in_db = Payment()
    payment_in_db = set_model_from_another_model(from_model=payment, to_model=payment_in_db)
    db.add(payment_in_db)
    db.commit()
    db.refresh(payment_in_db)
    return payment_in_db

def update_payment(payment: PaymentUpdate, db: Session = Depends(get_session)) -> Payment | None:
    payment_in_db = db.get(Payment, payment.payment_id)
    payment_in_db = set_model_from_another_model(from_model=payment, to_model=payment_in_db)
    db.add(payment_in_db)
    db.commit()
    db.refresh(payment_in_db)
    return payment_in_db


def get_recursive_payment_charge(recursive_payment_charge_id: int, db: Session = Depends(get_session)) -> RecursivePaymentCharge | None:
    charge = db.get(RecursivePaymentCharge, recursive_payment_charge_id)
    return charge

def create_recursive_payment_charge(charge: RecursivePaymentChargeCreate,
                                    db: Session = Depends(get_session)) -> RecursivePaymentCharge | None:
    charge_in_db = RecursivePaymentCharge()
    charge_in_db = set_model_from_another_model(from_model=charge, to_model=charge_in_db)
    db.add(charge_in_db)
    db.commit()
    db.refresh(charge_in_db)
    return charge_in_db


def update_recursive_payment_charge(charge: RecursivePaymentChargeUpdate,
                                    db: Session = Depends(get_session)) -> RecursivePaymentCharge | None:
    charge_in_db = db.get(RecursivePaymentCharge, charge.recursive_payment_charge_id)
    charge_in_db = set_model_from_another_model(from_model=charge, to_model=charge_in_db)
    db.commit()
    db.refresh(charge_in_db)
    return charge_in_db


def get_needed_to_run_payment_charges(db: Session = Depends(get_session)) -> list[RecursivePaymentCharge] | None:
    statement = select(RecursivePaymentCharge).where(RecursivePaymentCharge.datetime_to_charge <= datetime.utcnow(),
                                                     RecursivePaymentCharge.active,
                                                     RecursivePaymentCharge.successful==False)
    charges = db.exec(statement).all()
    return charges


def get_my_payment_charges(db: Session = Depends(get_session), user: User = Depends(current_active_user)):
    statement = select(RecursivePaymentCharge).where(RecursivePaymentCharge.user_id == user.id,
                                                     RecursivePaymentCharge.active,
                                                     )
    charges = db.exec(statement).all()
    return charges


def set_my_payment_charges_inactive(db: Session = Depends(get_session), user: User = Depends(current_active_user)):
    statement = select(RecursivePaymentCharge).where(RecursivePaymentCharge.user_id == user.id,
                                                     RecursivePaymentCharge.active,
                                                     )
    charges = db.exec(statement).all()
    for charge in charges:
        charge.active = False
    db.commit()
    return charges

def set_payment_charges_of_user_inactive(user_id: UUID4, db: Session = Depends(get_session)):
    statement = select(RecursivePaymentCharge).where(RecursivePaymentCharge.user_id == user_id,
                                                     RecursivePaymentCharge.active,
                                                     )
    charges = db.exec(statement).all()
    for charge in charges:
        charge.active = False
    db.commit()
    return charges

