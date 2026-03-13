from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from database.db import Base
import datetime

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    amount = Column(Float)
    payment_type = Column(String) # featured_listing, contact_unlock
    status = Column(String) # pending, completed, failed
    razorpay_order_id = Column(String, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
