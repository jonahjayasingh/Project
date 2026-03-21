import razorpay
from sqlalchemy.orm import Session
from models.payment import Payment
from models.pet import Pet
from schemas.payment_schema import PaymentCreate, PaymentVerify

# Razorpay credentials - In production, these should be environment variables
<<<<<<< HEAD
RAZORPAY_KEY_ID = "rzp_test_your_key_id"
RAZORPAY_KEY_SECRET = "your_key_secret"
=======
RAZORPAY_KEY_ID ="rzp_test_SHY9NaXwt3rP5e"
RAZORPAY_KEY_SECRET = "snECQKa7OGUw8ltfrBqtoPbc"
>>>>>>> fac2c57 (add)

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def create_order(db: Session, payment_data: PaymentCreate, user_id: int):
<<<<<<< HEAD
=======
    # If featured_listing, check if already featured
    if payment_data.payment_type == "featured_listing" and payment_data.pet_id:
        pet = db.query(Pet).filter(Pet.id == payment_data.pet_id).first()
        if pet and pet.is_featured:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Pet is already featured")

>>>>>>> fac2c57 (add)
    # Convert amount to paise (1 INR = 100 paise)
    amount_in_paise = int(payment_data.amount * 100)
    
    order_data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": "1"
    }
    
<<<<<<< HEAD
    razorpay_order = client.order.create(data=order_data)
=======
    try:
        razorpay_order = client.order.create(data=order_data)
    except Exception as e:
        from fastapi import HTTPException
        print(f"Razorpay Order Error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create Razorpay order: {str(e)}")
>>>>>>> fac2c57 (add)
    
    db_payment = Payment(
        user_id=user_id,
        pet_id=payment_data.pet_id,
        amount=payment_data.amount,
        payment_type=payment_data.payment_type,
        status="pending",
        razorpay_order_id=razorpay_order['id']
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return {
        "order_id": razorpay_order['id'],
        "amount": razorpay_order['amount'],
        "currency": razorpay_order['currency'],
<<<<<<< HEAD
=======
        "razorpay_key": RAZORPAY_KEY_ID,
>>>>>>> fac2c57 (add)
        "payment_id": db_payment.id
    }

def verify_payment_signature(db: Session, verify_data: PaymentVerify):
    params_dict = {
        'razorpay_order_id': verify_data.razorpay_order_id,
        'razorpay_payment_id': verify_data.razorpay_payment_id,
        'razorpay_signature': verify_data.razorpay_signature
    }
    
    try:
        client.utility.verify_payment_signature(params_dict)
        
        # Update payment status in DB
        db_payment = db.query(Payment).filter(Payment.razorpay_order_id == verify_data.razorpay_order_id).first()
        if db_payment:
            db_payment.status = "completed"
            db_payment.razorpay_payment_id = verify_data.razorpay_payment_id
            
            # If it's a featured listing, update the pet model
            if db_payment.payment_type == "featured_listing" and db_payment.pet_id:
                db_pet = db.query(Pet).filter(Pet.id == db_payment.pet_id).first()
                if db_pet:
                    db_pet.is_featured = True
            
            db.commit()
            return True
    except Exception as e:
        print(f"Payment verification failed: {e}")
        return False
    return False
