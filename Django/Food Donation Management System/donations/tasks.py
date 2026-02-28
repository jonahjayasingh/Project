from celery import shared_task
from django.utils import timezone
from .models import Donation
from .utils import send_donation_email
from django.db.models import Q

@shared_task
def check_expired_donations():
    """
    Background process checks expired donations periodically
    """
    now = timezone.now()
    expired_donations = Donation.objects.filter(
        expiry_time__lte=now,
        status__in=['Pending', 'Accepted'],
        is_archived=False
    ).exclude(status='Expired')
    
    for donation in expired_donations:
        donation.status = 'Expired'
        donation.save()
        
        # Notify Donor
        send_donation_email(
            "Donation Expired",
            "donation_expired",
            {'donation': donation},
            [donation.donor.email]
        )

@shared_task
def send_expiry_reminders():
    """
    Send alerts when food is nearing expiry (within 1 hour)
    """
    now = timezone.now()
    near_expiry = Donation.objects.filter(
        expiry_time__lte=now + timezone.timedelta(hours=1),
        expiry_time__gt=now,
        status__in=['Pending', 'Accepted'],
        is_archived=False
    )
    
    for donation in near_expiry:
        # Notify nearby NGOs to prioritize pickup
        # For simplicity, we can log this or send to all NGOs who can see it
        # Real logic would use distance filtering like in the dashboard
        pass

@shared_task
def cleanup_old_records():
    """
    Archive completed or old donations
    """
    limit = timezone.now() - timezone.timedelta(days=30)
    Donation.objects.filter(
        Q(status='Delivered') | Q(status='Expired'),
        updated_at__lte=limit,
        is_archived=False
    ).update(is_archived=True)
