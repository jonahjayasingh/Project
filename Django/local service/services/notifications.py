from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

def send_intelligent_notification(user, title, message, notification_type='SYSTEM', send_email=True):
    """
    Unified Notification System: In-app + Email
    """
    # 1. Create In-App Notification
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type
    )
    
    # 2. Send Email (if enabled and user has email)
    if send_email and user.email:
        try:
            subject = f"[ServiceFinder] {title}"
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            print(f"Email Error: {e}")

def notify_booking_status(booking):
    """
    Automatic status update notifications
    """
    subjects = {
        'ACCEPTED': "Booking Accepted! ✅",
        'CANCELLED': "Booking Cancelled ❌",
        'COMPLETED': "Job Completed! ⭐",
        'PENDING': "New Booking Request 📩"
    }
    
    title = subjects.get(booking.status, "Booking Update")
    
    if booking.status == 'PENDING':
        # Notify Provider
        msg = f"Hello {booking.provider.name}, you have a new request from {booking.user.username} for {booking.date} at {booking.time_slot}."
        send_intelligent_notification(booking.provider.user, title, msg, 'BOOKING')
    else:
        # Notify Client
        msg = f"Your booking with {booking.provider.name} for {booking.date} has been updated to: {booking.status}."
        send_intelligent_notification(booking.user, title, msg, 'BOOKING')
