import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.models import StaticPage, SystemSetting

def seed_static():
    pages = [
        {
            'slug': 'about-us',
            'title': 'About Lab Secure',
            'content': """
                Lab Secure is a next-generation Laboratory Management System (LMS) designed to bridge the gap between patients and diagnostic centers. 
                Our platform provides a secure, transparent, and efficient way to book medical tests, manage reports, and ensure timely healthcare delivery.
                
                Founded in 2026, we utilize cutting-edge technology to maintain the highest standards of data security and patient privacy. 
                Our network includes only verified and licensed laboratories, ensuring that you receive accurate results every time.
            """
        },
        {
            'slug': 'faq',
            'title': 'Frequently Asked Questions',
            'content': """
                ### 1. How do I book a test?
                Simply register as a patient, search for a lab near you, and select the desired test and time slot.
                
                ### 2. When will I get my report?
                Most reports are uploaded within 24-48 hours. You will receive a notification as soon as your report is ready.
                
                ### 3. How do I pay for the tests?
                Currently, we follow a manual payment verification system. You need to upload the transaction proof (screenshot) after making the payment to the lab's account.
                
                ### 4. Can I reschedule my appointment?
                Yes, you can reschedule your appointment from the dashboard as long as the payment has not been verified.
            """
        },
        {
            'slug': 'privacy-policy',
            'title': 'Privacy & Data Security',
            'content': """
                At Lab Secure, your health data is your own. We implement end-to-end encryption for report storage and strict role-based access control.
                
                *   We do not share your medical records with third parties.
                *   All uploads are scanned for security.
                *   Technicians only see the data necessary for processing your tests.
            """
        }
    ]

    for p in pages:
        obj, created = StaticPage.objects.update_or_create(
            slug=p['slug'],
            defaults={'title': p['title'], 'content': p['content']}
        )
        print(f"Page {p['slug']} {'created' if created else 'updated'}.")

    settings = [
        ('maintenance_mode', 'False', 'If True, only admins can access the site.'),
        ('allow_new_registrations', 'True', 'Allow new patient/lab signups.'),
        ('report_retention_days', '365', 'Number of days to keep historical reports.'),
        ('support_email', 'admin@labsecure.com', 'Global support contact email.')
    ]

    for key, val, desc in settings:
        obj, created = SystemSetting.objects.update_or_create(
            key=key,
            defaults={'value': val, 'description': desc}
        )
        print(f"Setting {key} {'created' if created else 'updated'}.")

if __name__ == "__main__":
    seed_static()
