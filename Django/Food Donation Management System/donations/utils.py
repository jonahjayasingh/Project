from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_donation_email(subject, template_name, context, recipient_list):
    """
    Helper to send HTML emails
    """
    try:
        html_message = render_to_string(f'donations/emails/{template_name}.html', context)
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            html_message=html_message,
            fail_silently=True
        )
    except Exception as e:
        print(f"Error sending email: {e}")

def log_system_activity(action, user=None, details=None):
    from tracking.models import SystemLog
    try:
        SystemLog.objects.create(
            action=action,
            performed_by=user,
            details=details
        )
    except Exception as e:
        print(f"Error logging activity: {e}")
