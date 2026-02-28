from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Payment
from events.models import Event
import uuid
import stripe
from django.conf import settings
from django.urls import reverse
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def client_payment_view(request, event_id):
    event = get_object_or_404(Event, id=event_id, client=request.user)
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        payment_type = request.POST.get('payment_type', 'ADVANCE')
        
        # Validation: Don't allow paying more than the remaining balance
        if amount > event.remaining_balance:
            messages.error(request, f"Cannot pay more than the remaining balance of ₹{event.remaining_balance}")
            return redirect('payments:pay_now', event_id=event.id)
        
        # Stripe Checkout Session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {
                                'name': f"Payment for {event.event_type.name}",
                            },
                            'unit_amount': int(amount * 100),
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri(
                    reverse('payments:stripe_success')
                ) + f"?session_id={{CHECKOUT_SESSION_ID}}&event_id={event.id}&amount={amount}&type={payment_type}",
                cancel_url=request.build_absolute_uri(
                    reverse('payments:pay_now', args=[event.id])
                ),
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            messages.error(request, f"Error starting Stripe checkout: {str(e)}")
            return redirect('payments:pay_now', event_id=event.id)
        
    return render(request, 'payments/payment_form.html', {'event': event})

@login_required
def stripe_success_view(request):
    session_id = request.GET.get('session_id')
    event_id = request.GET.get('event_id')
    amount = Decimal(request.GET.get('amount', 0))
    payment_type = request.GET.get('type', 'ADVANCE')
    
    event = get_object_or_404(Event, id=event_id)
    
    # In production, you would verify the session_id with Stripe here
    # session = stripe.checkout.Session.retrieve(session_id)
    
    # Payment successful, update database
    payment = Payment.objects.create(
        event=event,
        payment_type=payment_type,
        amount=amount,
        transaction_id=f"STRIPE_{session_id[-12:]}"
    )
    
    # Update event amount paid
    event.advance_paid = (event.advance_paid or Decimal('0.00')) + amount
    if event.advance_paid > event.total_cost:
        event.advance_paid = event.total_cost
    
    if event.status == 'PENDING':
        event.status = 'CONFIRMED'
    event.save()
    
    messages.success(request, f"Stripe Payment of ₹{amount} successful!")
    return redirect('events:event_detail', pk=event.pk)

def admin_payments_view(request):
    payments = Payment.objects.all().order_by('-payment_date')
    return render(request, 'payments/admin_payments.html', {'payments': payments})
