# Library Management System

A comprehensive Django-based Library Management System with role-based access control, book borrowing/returning functionality, and automated student number generation.

## Features

### 🔐 Authentication & Authorization
- **Admin/Librarian Role**: Full access to manage students, books, and borrow records
- **Student Role**: Can browse books, borrow books, and view their borrowed books
- Secure login/logout functionality
- Role-based dashboard redirection

### 👥 Student Management
- **Auto-generated unique student numbers** (format: STU + 8-character UUID)
- Create, read, update, and delete student profiles
- Track student information:
  - Name
  - Email
  - Department
  - Class
  - Maximum books allowed (configurable)
  - Date created
- Search students by number, name, email, or department

### 📚 Book Management
- Add, edit, and delete books
- Track book inventory:
  - Title
  - Author
  - ISBN (unique identifier)
  - Total copies
  - Available copies
  - Description
- Search books by title, author, or ISBN
- Automatic inventory management

### 📖 Borrowing System
- **Smart validation**:
  - Check student borrowing limit
  - Verify book availability
  - Prevent duplicate borrows
- **Automatic tracking**:
  - Borrow date (auto-set)
  - Due date (14 days from borrow)
  - Return date
  - Status (borrowed/returned/overdue)
- **Overdue detection**: Automatically marks books as overdue
- **Inventory updates**: Automatically adjusts available copies

### 📊 Admin Dashboard
- Real-time statistics:
  - Total students
  - Total books
  - Currently borrowed books
  - Overdue books
- Recent borrow activity
- Quick action buttons

### 🎓 Student Dashboard
- View student number and profile
- See borrowed books with due dates
- Status indicators (borrowed/overdue)
- Browse available books
- One-click book borrowing
- Return books directly

### 🔍 Search & Filter
- Search students by multiple criteria
- Search books by title, author, or ISBN
- Filter borrow history by status
- Real-time search results

## Technology Stack

- **Backend**: Django 5.2.5
- **Database**: SQLite (development)
- **Frontend**: HTML5, CSS3 (Vanilla)
- **Design**: Modern gradient UI with animations
- **Authentication**: Django's built-in auth system

## Installation & Setup

### Prerequisites
- Python 3.10+
- Virtual environment activated

### Setup Steps

1. **Activate virtual environment**:
   ```bash
   source /Volumes/CrucialX9/Project/venv/bin/activate
   ```

2. **Install dependencies** (if needed):
   ```bash
   pip install django
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Set up demo data**:
   ```bash
   python manage.py setup_demo
   ```

5. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the application**:
   - Open browser: http://127.0.0.1:8000/

## Demo Accounts

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Full system access, can manage students and books

### Student Accounts
- **Username**: `student1` / `student2` / `student3`
- **Password**: `student123`
- **Access**: Can browse and borrow books

## Usage Guide

### For Admins/Librarians

1. **Login** with admin credentials
2. **Add Students**:
   - Navigate to "Students" → "Add New Student"
   - Fill in student details and create account
   - Student number is auto-generated
3. **Add Books**:
   - Navigate to "Books" → "Add New Book"
   - Enter book details and inventory count
4. **Manage Borrowing**:
   - View all borrow records in "History"
   - Mark books as returned
   - Filter by status (borrowed/returned/overdue)
5. **Monitor System**:
   - Dashboard shows real-time statistics
   - Track overdue books
   - View recent activity

### For Students

1. **Login** with student credentials
2. **View Dashboard**:
   - See your student number
   - Check borrowed books and due dates
   - Monitor borrowing limit
3. **Browse Books**:
   - Click "Browse Books"
   - Search for books by title, author, or ISBN
   - See available copies
4. **Borrow Books**:
   - Click "Borrow" on available books
   - System validates your borrowing limit
   - Due date is automatically set (14 days)
5. **Return Books**:
   - Go to dashboard
   - Click "Return Book" on borrowed items
   - Book becomes available immediately

## Business Rules

### Borrowing Limits
- Default: 3 books per student (configurable)
- Cannot borrow if limit is reached
- Cannot borrow the same book twice simultaneously

### Book Availability
- Books can only be borrowed if available copies > 0
- Available copies automatically decrease on borrow
- Available copies automatically increase on return

### Due Dates & Overdue
- Loan period: 14 days
- Overdue status automatically applied after due date
- Overdue books highlighted in red

### Validation
- Unique student numbers (auto-generated)
- Unique ISBN per book
- Unique email per student
- Available copies cannot exceed total copies

## Project Structure

```
Library_management_system/
├── library/                          # Main app
│   ├── management/
│   │   └── commands/
│   │       └── setup_demo.py        # Demo data setup
│   ├── migrations/                   # Database migrations
│   ├── templates/
│   │   └── library/                 # All HTML templates
│   ├── admin.py                     # Admin interface config
│   ├── models.py                    # Data models
│   ├── views.py                     # View logic
│   └── urls.py                      # URL routing
├── library_system/                   # Project settings
│   ├── settings.py                  # Django settings
│   └── urls.py                      # Root URL config
├── db.sqlite3                       # Database
└── manage.py                        # Django management script
```

## Models

### Student
- `user` (OneToOne with User)
- `student_number` (auto-generated, unique)
- `name`
- `email` (unique)
- `department`
- `class_name`
- `date_created`
- `max_books_allowed`

### Book
- `title`
- `author`
- `isbn` (unique)
- `total_copies`
- `available_copies`
- `description`
- `date_added`

### BorrowRecord
- `student` (ForeignKey)
- `book` (ForeignKey)
- `borrow_date` (auto-set)
- `due_date`
- `return_date`
- `status` (borrowed/returned/overdue)
- `notes`

## Design Features

### Modern UI/UX
- ✨ Gradient backgrounds
- 🎨 Color-coded status badges
- 📊 Statistical cards with hover effects
- 🔔 Toast notifications for actions
- 📱 Responsive design
- ⚡ Smooth animations and transitions

### User Experience
- Intuitive navigation
- Clear action buttons
- Search functionality on all list pages
- Empty state messages
- Confirmation dialogs for deletions
- Real-time validation feedback

## Admin Interface

Access Django admin at: http://127.0.0.1:8000/admin/

Features:
- Advanced filtering and searching
- Bulk actions
- Readonly fields for auto-generated data
- Custom displays for related data
- Date hierarchy for borrow records

## Future Enhancements

Potential features to add:
- [ ] Email notifications for due dates
- [ ] Fine calculation for overdue books
- [ ] Book reservation system
- [ ] Reading history and recommendations
- [ ] Export reports (PDF/Excel)
- [ ] Book categories and genres
- [ ] Advanced search filters
- [ ] Student ID card generation
- [ ] QR code for books
- [ ] Mobile app integration

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill -9
python manage.py runserver
```

### Database issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py setup_demo
```

### Missing dependencies
```bash
pip install django
```

## License

This project is created for educational purposes.

## Support

For issues or questions, please refer to the Django documentation:
- https://docs.djangoproject.com/

---

**Built with ❤️ using Django**
