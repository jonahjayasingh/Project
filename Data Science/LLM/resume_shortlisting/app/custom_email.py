import smtplib
from email.message import EmailMessage
from django.conf import settings

def send_application_confirmation(applicant_email, applicant_name, role, website_name="AI-Powered Resume Shortlisting System",
                                  smtp_server="smtp.gmail.com", smtp_port=587, sender_email=settings.EMAIL_HOST_USER, sender_password=settings.EMAIL_HOST_PASSWORD):

    name_part = applicant_name if applicant_name else "Applicant"

    msg = EmailMessage()
    msg["Subject"] = "Your Application Has Been Received"
    msg["From"] = sender_email
    msg["To"] = applicant_email

    msg.set_content(
        f"""Hello {name_part},

This message confirms that we have received your application for the role of {role} submitted through {website_name}.

We will review your materials and contact you if additional information is needed.

Best regards,
Hiring Team
"""
    )

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

    print("Confirmation email sent.")
