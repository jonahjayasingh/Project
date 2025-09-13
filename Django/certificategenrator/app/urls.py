from django.urls import path,reverse_lazy
from .views import *
from django.contrib.auth import views as auth_views
from django.conf import settings


app_name = "app"


urlpatterns = [
  
    path("",home, name="home"),
    path("login",user_login, name="login"),
    path("register",user_register, name="register"),
    path("logout",user_logout, name="logout"),
    path("dashboard",dashboard, name="dashboard"),
    path("add_student",add_student, name="add_student"),
    path("edit_student",edit_student, name="edit_student"),
    path("alumni",search_alumni, name="search_alumni"),
    path("generate_certificate",get_certificate, name="generate_certificate"),
    path("show_certificate/<str:location>",show_certificate, name="show_certificate"),
    path("get_in_touch",get_in_touch, name="get_in_touch"),
    path("add_receipt",add_receipt, name="add_receipt"),
    path("show_receipt/<str:location>",show_receipt, name="show_receipt"),
    path("search_student",search_student, name="search_student"),
    path("single_student/<int:student_id>",single_student, name="single_student"),
    path("delete_student/<int:student_id>",delete_student, name="delete_student"),
    path("payment",payment, name="payment"),
    path("staff",staff,name="staff"),
    path("update_permission",update_permission,name="update_permission"),
    path("make_staff",make_staff,name="make_staff"),
    path("delete_user",delete_user, name="delete_user" ),
    path("account",account, name="account"),
    path("credit",transaction, name="credit"),
    path("transaction",transaction, name="transaction"),
    path("excel",display_excel,name="excel"),
    path("payment_excel",display_payment_excel, name="payment_excel"),
    path("download_student_details",download_student_details, name="download_student_details"),
    path("update_staff",update_staff,name="update_staff"),
    path("course",add_course,name="course"),
    path("delete_course/<int:id>",delete_course,name="delete_course"),
    path("edit_course",edit_course,name="edit_course"),
    path("staff_details",staff_details,name="staff_details"),
    path("all_staff",all_staff,name="all_staff"),
    path("work_updation",WorkView,name="work_updation"),
    path("attendance",attendance,name="attendance"),
    path("download_attendance",download_attendance,name="download_attendance"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",  # this shows the form
            subject_template_name="registration/password_reset_subject.txt",
            html_email_template_name="registration/password_reset_email.html",
            success_url=reverse_lazy("app:password_reset_done")
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("app:password_reset_complete")
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
