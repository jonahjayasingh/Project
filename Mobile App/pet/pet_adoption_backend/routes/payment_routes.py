from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.user import User
from schemas.payment_schema import PaymentCreate, PaymentVerify, PaymentOut
from services.payment_service import create_order, verify_payment_signature
from routes.auth_routes import get_current_user

router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/create-order")
def initiate_payment(payment_data: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_order(db, payment_data, current_user.id)

@router.post("/verify")
def verify_payment(verify_data: PaymentVerify, db: Session = Depends(get_db)):
    success = verify_payment_signature(db, verify_data)
    if not success:
        raise HTTPException(status_code=400, detail="Payment verification failed")
    return {"message": "Payment successful"}
