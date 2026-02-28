from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('submit/<int:event_id>/', views.submit_feedback_view, name='submit'),
    path('admin/list/', views.admin_feedback_list_view, name='admin_list'),
]
