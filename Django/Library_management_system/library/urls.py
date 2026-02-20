from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Student URLs
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('books/', views.available_books, name='available_books'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Student Management
    path('students/', views.manage_students, name='manage_students'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:student_id>/', views.delete_student, name='delete_student'),
    
    # Book Management
    path('books/manage/', views.manage_books, name='manage_books'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    
    # Request Management
    path('requests/pending/', views.pending_requests, name='pending_requests'),
    path('requests/approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('requests/reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('requests/handover/<int:request_id>/', views.handover_book, name='handover_book'),
    
    # Borrow History
    path('history/', views.borrow_history, name='borrow_history'),
]
