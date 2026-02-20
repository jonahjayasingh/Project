from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import Student, Book, BorrowRecord


# Helper functions for role checking
def is_admin(user):
    """Check if user is admin/librarian"""
    return user.is_staff or user.groups.filter(name='Librarian').exists()


def is_student(user):
    """Check if user is a student"""
    return hasattr(user, 'student_profile')


# Home View
def home(request):
    """Home page - landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'library/home.html')


# Authentication Views
def login_view(request):
    """Login view for all users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'library/login.html')



@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def change_password(request):
    """Change password for logged-in users"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'library/change_password.html')
        
        # Validate new password
        if len(new_password) < 6:
            messages.error(request, 'New password must be at least 6 characters long.')
            return render(request, 'library/change_password.html')
        
        # Validate password confirmation
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'library/change_password.html')
        
        # Change password
        request.user.set_password(new_password)
        request.user.save()
        
        # Update session to prevent logout
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Your password has been changed successfully!')
        return redirect('dashboard')
    
    return render(request, 'library/change_password.html')


@login_required
@user_passes_test(is_student, login_url='login')
def student_profile(request):
    """Student profile view (read-only)"""
    student = request.user.student_profile
    
    # Get statistics
    total_borrowed = BorrowRecord.objects.filter(
        student=student,
        status__in=['borrowed', 'overdue']
    ).count()
    
    total_returned = BorrowRecord.objects.filter(
        student=student,
        status='returned'
    ).count()
    
    pending_requests = BorrowRecord.objects.filter(
        student=student,
        status='pending'
    ).count()
    
    context = {
        'student': student,
        'total_borrowed': total_borrowed,
        'total_returned': total_returned,
        'pending_requests': pending_requests,
    }
    return render(request, 'library/student_profile.html', context)


@login_required
def dashboard(request):
    """Main dashboard - redirects based on user role"""
    if is_admin(request.user):
        return redirect('admin_dashboard')
    elif is_student(request.user):
        return redirect('student_dashboard')
    else:
        messages.error(request, 'You do not have access to any dashboard.')
        return redirect('login')


# Student Views
@login_required
@user_passes_test(is_student, login_url='login')
def student_dashboard(request):
    """Student dashboard showing profile and borrowed books"""
    student = request.user.student_profile
    borrowed_books = BorrowRecord.objects.filter(
        student=student, 
        status__in=['borrowed', 'overdue']
    )
    
    # Get pending and approved requests
    pending_requests = BorrowRecord.objects.filter(student=student, status='pending')
    approved_requests = BorrowRecord.objects.filter(student=student, status='approved')
    
    # Update overdue status
    for record in borrowed_books:
        if record.is_overdue():
            record.status = 'overdue'
            record.save()
    
    context = {
        'student': student,
        'borrowed_books': borrowed_books,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'can_borrow_more': student.can_borrow_more_books(),
        'books_borrowed_count': student.get_borrowed_books_count(),
    }
    return render(request, 'library/student_dashboard.html', context)


@login_required
@user_passes_test(is_student, login_url='login')
def available_books(request):
    """View available books for students"""
    search_query = request.GET.get('search', '')
    
    books = Book.objects.filter(available_copies__gt=0)
    
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    context = {
        'books': books,
        'search_query': search_query,
    }
    return render(request, 'library/available_books.html', context)


@login_required
@user_passes_test(is_student, login_url='login')
def borrow_book(request, book_id):
    """Request to borrow a book"""
    student = request.user.student_profile
    book = get_object_or_404(Book, id=book_id)
    
    # Validation checks
    if not student.can_borrow_more_books():
        messages.error(request, f'You have reached the maximum limit of {student.max_books_allowed} books (including pending requests).')
        return redirect('available_books')
    
    if not book.is_available():
        messages.error(request, 'This book is currently not available.')
        return redirect('available_books')
    
    # Check if student already has a pending or active request for this book
    existing_request = BorrowRecord.objects.filter(
        student=student,
        book=book,
        status__in=['pending', 'approved', 'borrowed', 'overdue']
    ).exists()
    
    if existing_request:
        messages.error(request, 'You already have a pending or active request for this book.')
        return redirect('available_books')
    
    if request.method == 'POST':
        requested_days = int(request.POST.get('requested_days', 14))
        notes = request.POST.get('notes', '')
        
        # Create borrow request
        BorrowRecord.objects.create(
            student=student,
            book=book,
            requested_days=requested_days,
            notes=notes,
            status='pending'
        )
        
        messages.success(request, f'Request submitted for "{book.title}". The librarian will review your request.')
        return redirect('student_dashboard')
    
    # Show request form
    context = {'book': book}
    return render(request, 'library/request_book.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def return_book(request, record_id):
    """Return a borrowed book - Admin/Librarian only"""
    record = get_object_or_404(BorrowRecord, id=record_id)
    
    if record.status == 'returned':
        messages.warning(request, 'This book has already been returned.')
        return redirect('dashboard')
    
    # Update record
    record.return_date = timezone.now()
    record.status = 'returned'
    record.save()
    
    # Update available copies
    book = record.book
    book.available_copies += 1
    book.save()
    
    messages.success(request, f'Successfully returned "{book.title}" for {record.student.name}.')
    return redirect('borrow_history')


# Request Management Views
@login_required
@user_passes_test(is_admin, login_url='login')
def pending_requests(request):
    """View all pending book requests"""
    requests = BorrowRecord.objects.filter(status='pending').select_related('student', 'book')
    
    context = {
        'requests': requests,
    }
    return render(request, 'library/pending_requests.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def approve_request(request, request_id):
    """Approve a book request"""
    borrow_request = get_object_or_404(BorrowRecord, id=request_id, status='pending')
    
    borrow_request.status = 'approved'
    borrow_request.approved_by = request.user
    borrow_request.approved_date = timezone.now()
    # Calculate due date based on requested days
    borrow_request.due_date = timezone.now().date() + timedelta(days=borrow_request.requested_days)
    borrow_request.save()
    
    messages.success(request, f'Request approved for {borrow_request.student.name} to borrow "{borrow_request.book.title}". Due date: {borrow_request.due_date}')
    return redirect('pending_requests')


@login_required
@user_passes_test(is_admin, login_url='login')
def reject_request(request, request_id):
    """Reject a book request"""
    borrow_request = get_object_or_404(BorrowRecord, id=request_id, status='pending')
    
    if request.method == 'POST':
        admin_notes = request.POST.get('admin_notes', '')
        borrow_request.status = 'rejected'
        borrow_request.admin_notes = admin_notes
        borrow_request.save()
        
        messages.success(request, f'Request rejected for {borrow_request.student.name}.')
        return redirect('pending_requests')
    
    context = {'borrow_request': borrow_request}
    return render(request, 'library/reject_request.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def handover_book(request, request_id):
    """Hand over book to student (when they come to collect)"""
    borrow_request = get_object_or_404(BorrowRecord, id=request_id, status='approved')
    
    if request.method == 'POST':
        # Allow librarian to adjust due date if needed
        adjust_due_date = request.POST.get('adjust_due_date') == 'yes'
        admin_notes = request.POST.get('admin_notes', '')
        
        # Set borrow date
        borrow_request.borrow_date = timezone.now()
        
        # Adjust due date only if requested
        if adjust_due_date:
            return_days = int(request.POST.get('return_days', borrow_request.requested_days))
            borrow_request.due_date = timezone.now().date() + timedelta(days=return_days)
        # Otherwise keep the already-set due date from approval
        
        borrow_request.status = 'borrowed'
        borrow_request.admin_notes = admin_notes
        borrow_request.save()
        
        # Update available copies
        book = borrow_request.book
        book.available_copies -= 1
        book.save()
        
        messages.success(request, f'Book "{book.title}" handed over to {borrow_request.student.name}. Due date: {borrow_request.due_date}')
        return redirect('admin_dashboard')
    
    context = {'borrow_request': borrow_request}
    return render(request, 'library/handover_book.html', context)


# Admin Views
@login_required
@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    total_students = Student.objects.count()
    total_books = Book.objects.count()
    total_borrowed = BorrowRecord.objects.filter(status__in=['borrowed', 'overdue']).count()
    overdue_books = BorrowRecord.objects.filter(status='overdue').count()
    pending_requests = BorrowRecord.objects.filter(status='pending').count()
    
    # Get approved requests (ready for collection)
    approved_requests = BorrowRecord.objects.filter(status='approved').select_related('student', 'book')
    
    recent_borrows = BorrowRecord.objects.all().exclude(status__in=['pending', 'rejected', 'approved'])[:10]
    
    context = {
        'total_students': total_students,
        'total_books': total_books,
        'total_borrowed': total_borrowed,
        'overdue_books': overdue_books,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'recent_borrows': recent_borrows,
    }
    return render(request, 'library/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def manage_students(request):
    """Manage students - list and search"""
    search_query = request.GET.get('search', '')
    
    students = Student.objects.all()
    
    if search_query:
        students = students.filter(
            Q(student_number__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    
    context = {
        'students': students,
        'search_query': search_query,
    }
    return render(request, 'library/manage_students.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def add_student(request):
    """Add a new student"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        department = request.POST.get('department')
        class_name = request.POST.get('class_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'library/add_student.html')
        
        if Student.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'library/add_student.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create student profile
        student = Student.objects.create(
            user=user,
            name=name,
            email=email,
            department=department,
            class_name=class_name
        )
        
        messages.success(request, f'Student {student.student_number} created successfully!')
        return redirect('manage_students')
    
    return render(request, 'library/add_student.html')


@login_required
@user_passes_test(is_admin, login_url='login')
def edit_student(request, student_id):
    """Edit student details"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.email = request.POST.get('email')
        student.department = request.POST.get('department')
        student.class_name = request.POST.get('class_name')
        student.max_books_allowed = request.POST.get('max_books_allowed', 3)
        
        student.save()
        messages.success(request, 'Student updated successfully!')
        return redirect('manage_students')
    
    context = {'student': student}
    return render(request, 'library/edit_student.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def delete_student(request, student_id):
    """Delete a student"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        user = student.user
        student.delete()
        user.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('manage_students')
    
    context = {'student': student}
    return render(request, 'library/delete_student.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def manage_books(request):
    """Manage books - list and search"""
    search_query = request.GET.get('search', '')
    
    books = Book.objects.all()
    
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    context = {
        'books': books,
        'search_query': search_query,
    }
    return render(request, 'library/manage_books.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def add_book(request):
    """Add a new book"""
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        category = request.POST.get('category', 'other')
        total_copies = int(request.POST.get('total_copies', 1))
        description = request.POST.get('description', '')
        
        # Validation
        if Book.objects.filter(isbn=isbn).exists():
            messages.error(request, 'A book with this ISBN already exists.')
            return render(request, 'library/add_book.html')
        
        # Create book
        book = Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            total_copies=total_copies,
            available_copies=total_copies,
            description=description
        )
        
        messages.success(request, f'Book "{book.title}" added successfully!')
        return redirect('manage_books')
    
    return render(request, 'library/add_book.html')


@login_required
@user_passes_test(is_admin, login_url='login')
def edit_book(request, book_id):
    """Edit book details"""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.category = request.POST.get('category', 'other')
        book.description = request.POST.get('description', '')
        
        # Handle copies update
        old_total = book.total_copies
        new_total = int(request.POST.get('total_copies'))
        difference = new_total - old_total
        
        book.total_copies = new_total
        book.available_copies += difference
        
        # Ensure available copies don't go negative
        if book.available_copies < 0:
            book.available_copies = 0
        
        book.save()
        messages.success(request, 'Book updated successfully!')
        return redirect('manage_books')
    
    context = {'book': book}
    return render(request, 'library/edit_book.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def delete_book(request, book_id):
    """Delete a book"""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('manage_books')
    
    context = {'book': book}
    return render(request, 'library/delete_book.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def borrow_history(request):
    """View all borrow history"""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    records = BorrowRecord.objects.all()
    
    if status_filter:
        records = records.filter(status=status_filter)
    
    if search_query:
        records = records.filter(
            Q(student__student_number__icontains=search_query) |
            Q(student__name__icontains=search_query) |
            Q(book__title__icontains=search_query)
        )
    
    context = {
        'records': records,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'library/borrow_history.html', context)
