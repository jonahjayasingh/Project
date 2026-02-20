# Membership and Trainer Request System

## Overview
This system allows prospective members to request membership by choosing a plan, and existing members to request personal trainers.

## Features

### 1. Membership Requests
- **Public Access**: Anyone can request membership without logging in
- **Plan Selection**: Users can browse and select from available membership plans
- **Comprehensive Form**: Collects personal info, emergency contacts, health data, and fitness goals
- **Email Notifications**: Admins receive email notifications for new requests
- **Status Tracking**: Requests can be pending, approved, or rejected

### 2. Trainer Requests  
- **Member Access**: Only logged-in members can request trainers
- **Trainer Browse**: View all available trainers with their specializations
- **Preference Selection**: Choose specialization, preferred trainer, sessions per week, and time slots
- **Goal Setting**: Describe fitness goals and additional requirements
- **Email Notifications**: Admins receive email notifications for new requests
- **Status Tracking**: Requests can be pending, approved, or rejected

## URLs

### Membership Requests
- `/requests/membership/plans/` - View all membership plans
- `/requests/membership/request/` - Submit membership request
- `/requests/membership/request/<plan_id>/` - Submit request with pre-selected plan
- `/requests/membership/success/` - Success page after submission

### Trainer Requests
- `/requests/trainers/` - View all available trainers (login required)
- `/requests/trainer/request/` - Submit trainer request (login required)
- `/requests/trainer/request/<trainer_id>/` - Submit request with preferred trainer (login required)
- `/requests/trainer/success/` - Success page after submission

### My Requests
- `/requests/my-requests/` - View your own requests (login required)

## Models

### MembershipRequest
Fields:
- Personal Information: first_name, last_name, email, phone_number, date_of_birth, gender, address
- Emergency Contact: emergency_contact_name, emergency_contact_phone
- Health Information: blood_group, medical_notes, height, weight, fitness_goal
- Plan Selection: selected_plan (ForeignKey to MembershipPlan)
- Status: status (pending/approved/rejected), admin_notes, processed_by, processed_at
- Created User: created_user (linked after approval)

### TrainerRequest
Fields:
- Member: member (ForeignKey to Member)
- Preferences: preferred_specialization, preferred_trainer, sessions_per_week, preferred_time
- Goals: fitness_goals, additional_notes
- Status: status (pending/approved/rejected), admin_notes, assigned_trainer, processed_by, processed_at

## Admin Interface

Both models are registered in Django admin with:
- List displays showing key information
- Filters for status, dates, and other relevant fields
- Search functionality
- Organized fieldsets for easy data entry
- Readonly fields for timestamps

## Email Notifications

When a request is submitted:
1. System sends email to admin (configured in settings.EMAIL_RECIVER)
2. Email includes requester details and selected plan/preferences
3. Admin can then process the request in the admin panel

## Workflow

### Membership Request Workflow:
1. User visits membership plans page
2. Selects a plan and clicks "Request This Plan"
3. Fills out comprehensive membership form
4. Submits request
5. Admin receives email notification
6. Admin reviews request in admin panel
7. Admin approves/rejects request
8. If approved, admin creates user account and member profile

### Trainer Request Workflow:
1. Member logs in and views trainers list
2. Selects preferred trainer or specialization
3. Fills out trainer request form
4. Submits request
5. Admin receives email notification
6. Admin reviews request in admin panel
7. Admin assigns trainer and creates TrainerMemberAssignment
8. Member is notified of assigned trainer

## Next Steps

To complete the implementation:

1. **Run Migrations**: Stop the server and run:
   ```bash
   python manage.py makemigrations requests
   python manage.py migrate
   ```

2. **Create Templates**: Create the following template files:
   - `templates/requests/membership_plans.html`
   - `templates/requests/request_membership.html`
   - `templates/requests/membership_request_success.html`
   - `templates/requests/trainers_list.html`
   - `templates/requests/request_trainer.html`
   - `templates/requests/trainer_request_success.html`
   - `templates/requests/my_requests.html`

3. **Add Navigation Links**: Update your navigation to include:
   - "Join Now" or "Membership Plans" link for public users
   - "Request Trainer" link for logged-in members
   - "My Requests" link for members to track their requests

4. **Configure Email**: Update settings.py with proper email configuration for production

## Files Created

- `requests/models.py` - MembershipRequest and TrainerRequest models
- `requests/forms.py` - MembershipRequestForm and TrainerRequestForm
- `requests/views.py` - All view functions
- `requests/urls.py` - URL patterns
- `requests/admin.py` - Admin interface configuration
- `requests/apps.py` - App configuration
- `MEMBERSHIP_TRAINER_REQUESTS.md` - This documentation file

## Integration Points

- **Memberships App**: Links to MembershipPlan model
- **Members App**: Links to Member model
- **Trainers App**: Links to Trainer and TrainerMemberAssignment models
- **Accounts App**: Links to CustomUser model
- **Email System**: Uses Django email backend for notifications
