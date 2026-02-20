from django.urls import path
from . import views

app_name = 'requests'

urlpatterns = [
    # Membership requests
    path('membership/plans/', views.membership_plans_view, name='membership_plans'),
    path('membership/request/', views.request_membership_view, name='request_membership'),
    path('membership/request/<int:plan_id>/', views.request_membership_view, name='request_membership_with_plan'),
    path('membership/success/', views.membership_request_success_view, name='membership_request_success'),
    
    # Trainer requests
    path('trainers/', views.trainers_list_view, name='trainers_list'),
    path('trainer/request/', views.request_trainer_view, name='request_trainer'),
    path('trainer/request/<int:trainer_id>/', views.request_trainer_view, name='request_trainer_with_preference'),
    path('trainer/success/', views.trainer_request_success_view, name='trainer_request_success'),
    
    # My requests
    path('my-requests/', views.my_requests_view, name='my_requests'),
]
