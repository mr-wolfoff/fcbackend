from datetime import datetime
from pydantic import UUID4
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional


class PaymentBase(SQLModel):
    user_id: UUID4 = Field(foreign_key='user.id', unique=False, nullable=True)
    status: str = Field(default=None)
    payment_system_id: str = Field()
    status_payment_system: str = Field()
    payment_system: str = Field()
    payment_system_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    period: Optional[int] = Field(default=None)
    amount: Optional[float] = Field(default=None)
    first_payment_system_id: Optional[str] = Field(default=None)
    is_recurrent: Optional[bool] = Field(default=None)
    is_first_recurrent: Optional[bool] = Field(default=None)
    amount_after: Optional[float] = Field(default=None)
    period_after: Optional[int] = Field(default=None)
    pass

class Payment(PaymentBase, table=True):
    payment_id: int = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}, )

class PaymentRead(PaymentBase):
    payment_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(PaymentBase):
    payment_id: int



class RecursivePaymentChargeBase(SQLModel):
    user_id: UUID4 = Field(foreign_key='user.id', unique=False)
    payment_id: Optional[int] = Field()
    payment_system_id: Optional[str] = Field()
    datetime_to_charge: Optional[datetime] = Field()
    active: Optional[bool] = Field()
    successful: Optional[bool] = Field(default=False)
    amount: Optional[float] = Field(default=None)
    charge_tries: Optional[int] = Field(default=0)


class RecursivePaymentCharge(RecursivePaymentChargeBase, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}, )
    recursive_payment_charge_id: int = Field(primary_key=True)

class RecursivePaymentChargeCreate(RecursivePaymentChargeBase):
    pass

class RecursivePaymentChargeUpdate(RecursivePaymentChargeBase):
    recursive_payment_charge_id: int


class RecursivePaymentChargeRead(RecursivePaymentChargeBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    recursive_payment_charge_id: int
