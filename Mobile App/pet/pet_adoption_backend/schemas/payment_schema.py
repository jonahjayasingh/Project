from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    pet_id: Optional[int] = None
    amount: float
    payment_type: str # featured_listing, contact_unlock

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentOut(BaseModel):
    id: int
    user_id: int
    pet_id: Optional[int]
    amount: float
    payment_type: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
