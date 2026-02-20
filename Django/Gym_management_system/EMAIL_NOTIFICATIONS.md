# Email Notification System - Documentation

## Overview
The Gym Management System now sends automated email notifications for various events. All emails are currently configured to use the console backend for development, meaning they will appear in the terminal/console instead of being sent to actual email addresses.

## Email Configuration
**Location:** `Gym_management_system/settings.py` (Lines 151-158)

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = 'jayasinghjonah@gmail.com'
EMAIL_HOST_PASSWORD = 'uurzsjggqrxdghcg'
EMAIL_RECIVER = "jayasinghjonah24@gmail.com"
```

## Email Notifications Implemented

### 1. Member Registration Email
**Triggered:** When admin creates a new member
**Location:** `members/views.py` - `member_create()` function (Lines 101-169)

**Two emails are sent:**

#### A. Welcome Email to New Member
- **To:** New member's email address
- **Subject:** "Welcome to Our Gym!"
- **Content:**
  - Welcome message
  - Login credentials (username, email)
  - Login URL
  - Next steps (complete profile, check classes, etc.)
  - Contact information

#### B. Admin Notification
- **To:** Admin email (EMAIL_RECIVER)
- **Subject:** "New Member Registered - [Member Name]"
- **Content:**
  - Member's personal details
  - Health information
  - Emergency contact
  - Who registered the member
  - Registration date

### 2. Trainer Registration Email
**Triggered:** When admin creates a new trainer
**Location:** `trainers/views.py` - `trainer_create()` function (Lines 104-180)

**Two emails are sent:**

#### A. Welcome Email to New Trainer
- **To:** New trainer's email address
- **Subject:** "Welcome to Our Gym Team!"
- **Content:**
  - Welcome message
  - Login credentials (username, email)
  - Login URL
  - Professional profile details (specialization, experience, hourly rate)
  - Trainer capabilities and features
  - Contact information

#### B. Admin Notification
- **To:** Admin email (EMAIL_RECIVER)
- **Subject:** "New Trainer Registered - [Trainer Name]"
- **Content:**
  - Trainer's personal details
  - Professional information
  - Certifications
  - Availability status
  - Who registered the trainer
  - Registration date

### 3. Membership Request Email
**Triggered:** When someone submits a membership request from the public form
**Location:** `requests/views.py` - `request_membership_view()` function (Lines 37-56)

**Email sent:**
- **To:** Admin email (EMAIL_RECIVER)
- **Subject:** "New Membership Request - [Requester Name]"
- **Content:**
  - Requester's name, email, phone
  - Selected membership plan
  - Request to review in admin panel

### 4. Trainer Request Email
**Triggered:** When a member requests a personal trainer
**Location:** `requests/views.py` - `request_trainer_view()` function (Lines 117-136)

**Email sent:**
- **To:** Admin email (EMAIL_RECIVER)
- **Subject:** "New Trainer Request - [Member Name]"
- **Content:**
  - Member's name and email
  - Preferred specialization
  - Sessions per week
  - Request to review in admin panel

## Error Handling
All email sending operations are wrapped in try-except blocks with `fail_silently=True` to ensure that:
- The application continues to work even if email sending fails
- Errors are logged to console for debugging
- User experience is not interrupted

## Testing Emails

### Current Setup (Console Backend)
1. Start the Django development server
2. Perform an action that triggers an email (e.g., create a new member)
3. Check the terminal/console where the server is running
4. You'll see the email content printed there

### Example Console Output:
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Welcome to Our Gym!
From: jayasinghjonah@gmail.com
To: newmember@example.com
Date: Sat, 04 Jan 2026 19:30:00 +0530

Dear John Doe,

Welcome to our Gym Management System! Your account has been successfully created.
...
```

## Switching to Production Email

To send actual emails in production, update `settings.py`:

### For Gmail SMTP:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password, not regular password
```

### For Other SMTP Services:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yourprovider.com'
EMAIL_PORT = 587  # or 465 for SSL
EMAIL_USE_TLS = True  # or EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

## Email Templates (Future Enhancement)

Currently, emails use plain text format. For better presentation, you can:
1. Create HTML email templates in `templates/emails/`
2. Use Django's `render_to_string()` to generate HTML content
3. Use `EmailMultiAlternatives` to send both plain text and HTML versions

Example structure:
```
templates/
  emails/
    member_welcome.html
    member_welcome.txt
    trainer_welcome.html
    trainer_welcome.txt
```

## Security Notes

1. **Never commit real passwords to version control**
2. Use environment variables for sensitive data:
   ```python
   import os
   EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
   ```
3. For Gmail, use App Passwords instead of your regular password
4. Consider using services like SendGrid, Mailgun, or AWS SES for production

## Customization

To customize email content:
1. Locate the appropriate view function
2. Modify the `message` parameter in the `send_mail()` call
3. Update subject line, greeting, or any other content as needed

## Troubleshooting

### Emails not appearing in console:
- Check that `EMAIL_BACKEND` is set to console backend
- Ensure the development server is running
- Look for any error messages in the console

### Emails not sending in production:
- Verify SMTP credentials are correct
- Check firewall settings allow SMTP traffic
- Ensure EMAIL_USE_TLS or EMAIL_USE_SSL is set correctly
- Check spam folder for test emails
- Review server logs for error messages

## Summary

The email notification system is now fully integrated and will:
✅ Send welcome emails to new members and trainers
✅ Notify admins of new registrations
✅ Notify admins of membership and trainer requests
✅ Handle errors gracefully without breaking the application
✅ Work in development mode (console) and can be easily switched to production
