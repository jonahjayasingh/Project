from django.urls import path
from .views import *

app_name = "staff"

urlpatterns = [
    path("",staff_dashboard, name="staff_dashboard"),
    path("add_work",add_work, name="add_work"),
    path("edit_work",edit_work, name="edit_work"),
    path("add_student",add_student, name="add_student"),
    path("certificate/<str:location>",show_certificate, name="certificate" ),
    path("receipt/<str:location>",show_receipt, name="receipt" ),
    path("single_student/<int:id>",single_student, name="single_student" ),
    path("attendance",attendance, name="attendance" ),
    path("excel_view/",excel_view, name="excel_view" ),
    path("excel_attendance",excel_attendance, name="excel_attendance" ),
]
