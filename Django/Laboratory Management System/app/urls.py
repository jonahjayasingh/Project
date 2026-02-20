from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact_us, name="contact_us"),
    path("page/<slug:slug>/", views.static_page, name="static_page"),
    
    # Patient Views
    path("register/patient/", views.patient_register, name="patient_register"),
    path("register/lab/", views.lab_register, name="lab_register"),
    path("login/patient/", views.patient_login, name="patient_login"),
    path("login/lab/", views.lab_login, name="lab_login"),
    path("logout/", views.user_logout, name="logout"),
    
    # Dashboards
    path("dashboard/patient/", views.patient_dashboard, name="patient_dashboard"),
    path("dashboard/lab/", views.lab_dashboard, name="lab_dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    
    # Booking
    path("book-test/", views.book_test, name="book_test"),
    path("discover-labs/", views.lab_discovery, name="lab_discovery"),
    path("submit-review/<int:booking_id>/", views.submit_review, name="submit_review"),
    path("lab-reviews/", views.lab_reviews, name="lab_reviews"),
    path("booking-receipt/<int:booking_id>/", views.booking_receipt, name="booking_receipt"),
    path("ajax/load-tests/", views.load_tests, name="ajax_load_tests"),
    path("ajax/load-packages/", views.load_packages, name="ajax_load_packages"),
    path("upload-payment/<int:booking_id>/", views.upload_payment_proof, name="upload_payment_proof"),
    path("reschedule-booking/<int:booking_id>/", views.reschedule_booking, name="reschedule_booking"),
    path("cancel-booking/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("mark-no-show/<int:booking_id>/", views.mark_no_show, name="mark_no_show"),
    
    # Lab Management
    path("manage-tests/", views.manage_lab_tests, name="manage_lab_tests"),
    path("manage-packages/", views.manage_packages, name="manage_packages"),
    path("edit-package/<int:package_id>/", views.edit_package, name="edit_package"),
    path("lab-config/", views.lab_operations_config, name="lab_operations_config"),
    path("delete-package/<int:package_id>/", views.delete_package, name="delete_package"),
    path("manage-staff/", views.manage_staff, name="manage_staff"),
    path("edit-staff/<int:staff_id>/", views.edit_staff, name="edit_staff"),
    path("delete-staff/<int:staff_id>/", views.delete_staff, name="delete_staff"),
    path("assign-technician/<int:booking_id>/", views.assign_technician, name="assign_technician"),
    path("patients/", views.lab_patient_list, name="lab_patient_list"),
    path("edit-test/<int:test_id>/", views.edit_lab_test, name="edit_lab_test"),
    path("delete-test/<int:test_id>/", views.delete_lab_test, name="delete_lab_test"),
    path("update-status/<int:booking_id>/", views.update_booking_status, name="update_booking_status"),
    path("verify-payment/<int:booking_id>/", views.verify_payment, name="verify_payment"),
    path("upload-report/<int:booking_id>/", views.upload_report, name="upload_report"),
    path("report-history/<int:booking_id>/", views.report_history, name="report_history"),
    path("view-report/<int:booking_id>/", views.secure_report_serve, name="secure_report_serve"),
    path("view-report/<int:booking_id>/<int:version_id>/", views.secure_report_serve, name="secure_report_version_serve"),
    path("notifications/", views.notifications_list, name="notifications_list"),
    path("notifications/read/<int:n_id>/", views.mark_notification_read, name="mark_notification_read"),
    
    # Admin Management
    path("approve-lab/<int:lab_id>/", views.approve_lab, name="approve_lab"),
    path("toggle-lab-status/<int:lab_id>/", views.toggle_lab_status, name="toggle_lab_status"),
    path("admin/users/", views.admin_user_management, name="admin_user_management"),
    path("admin/settings/", views.system_settings, name="system_settings"),
    path("admin/analytics/export/", views.export_analytics, name="export_analytics"),
    path("admin/activity-logs/", views.admin_activity_logs, name="admin_activity_logs"),
]