import razorpay
from sqlalchemy.orm import Session
from models.payment import Payment
from models.pet import Pet
from schemas.payment_schema import PaymentCreate, PaymentVerify

# Razorpay credentials - In production, these should be environment variables
RAZORPAY_KEY_ID = "rzp_test_your_key_id"
RAZORPAY_KEY_SECRET = "your_key_secret"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def create_order(db: Session, payment_data: PaymentCreate, user_id: int):
    # Convert amount to paise (1 INR = 100 paise)
    amount_in_paise = int(payment_data.amount * 100)
    
    order_data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": "1"
    }
    
    razorpay_order = client.order.create(data=order_data)
    
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
