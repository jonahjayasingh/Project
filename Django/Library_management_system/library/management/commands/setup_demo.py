from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from library.models import Student, Book, BorrowRecord
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Set up demo data for the library system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up demo data...')
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@library.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created admin user (username: admin, password: admin123)'))
        else:
            self.stdout.write('Admin user already exists')
        
        # Create student users
        students_data = [
            {
                'username': 'student1',
                'name': 'John Doe',
                'email': 'john@student.com',
                'department': 'Computer Science',
                'class_name': 'CS-2024'
            },
            {
                'username': 'student2',
                'name': 'Jane Smith',
                'email': 'jane@student.com',
                'department': 'Mathematics',
                'class_name': 'MATH-2024'
            },
            {
                'username': 'student3',
                'name': 'Bob Johnson',
                'email': 'bob@student.com',
                'department': 'Physics',
                'class_name': 'PHY-2024'
            }
        ]
        
        for student_data in students_data:
            if not User.objects.filter(username=student_data['username']).exists():
                user = User.objects.create_user(
                    username=student_data['username'],
                    email=student_data['email'],
                    password='student123'
                )
                
                Student.objects.create(
                    user=user,
                    name=student_data['name'],
                    email=student_data['email'],
                    department=student_data['department'],
                    class_name=student_data['class_name']
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Created student: {student_data["name"]}'))
            else:
                self.stdout.write(f'Student {student_data["username"]} already exists')
        
        # Create books
        books_data = [
            {
                'title': 'Introduction to Algorithms',
                'author': 'Thomas H. Cormen',
                'isbn': '9780262033848',
                'total_copies': 5,
                'description': 'A comprehensive textbook on algorithms'
            },
            {
                'title': 'Clean Code',
                'author': 'Robert C. Martin',
                'isbn': '9780132350884',
                'total_copies': 3,
                'description': 'A handbook of agile software craftsmanship'
            },
            {
                'title': 'Design Patterns',
                'author': 'Erich Gamma',
                'isbn': '9780201633612',
                'total_copies': 4,
                'description': 'Elements of reusable object-oriented software'
            },
            {
                'title': 'The Pragmatic Programmer',
                'author': 'Andrew Hunt',
                'isbn': '9780135957059',
                'total_copies': 3,
                'description': 'Your journey to mastery'
            },
            {
                'title': 'Python Crash Course',
                'author': 'Eric Matthes',
                'isbn': '9781593279288',
                'total_copies': 6,
                'description': 'A hands-on, project-based introduction to programming'
            },
            {
                'title': 'Data Structures and Algorithms in Python',
                'author': 'Michael T. Goodrich',
                'isbn': '9781118290279',
                'total_copies': 4,
                'description': 'Comprehensive guide to data structures'
            },
            {
                'title': 'Artificial Intelligence: A Modern Approach',
                'author': 'Stuart Russell',
                'isbn': '9780134610993',
                'total_copies': 3,
                'description': 'The leading textbook in AI'
            },
            {
                'title': 'Database System Concepts',
                'author': 'Abraham Silberschatz',
                'isbn': '9780078022159',
                'total_copies': 5,
                'description': 'Comprehensive database systems textbook'
            }
        ]
        
        for book_data in books_data:
            if not Book.objects.filter(isbn=book_data['isbn']).exists():
                Book.objects.create(
                    title=book_data['title'],
                    author=book_data['author'],
                    isbn=book_data['isbn'],
                    total_copies=book_data['total_copies'],
                    available_copies=book_data['total_copies'],
                    description=book_data['description']
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Created book: {book_data["title"]}'))
            else:
                self.stdout.write(f'Book {book_data["title"]} already exists')
        
        # Create some sample borrow records
        if Student.objects.exists() and Book.objects.exists():
            student = Student.objects.first()
            books = Book.objects.all()[:2]
            
            for book in books:
                if not BorrowRecord.objects.filter(student=student, book=book, status='borrowed').exists():
                    if book.available_copies > 0:
                        due_date = timezone.now().date() + timedelta(days=14)
                        BorrowRecord.objects.create(
                            student=student,
                            book=book,
                            due_date=due_date,
                            status='borrowed'
                        )
                        book.available_copies -= 1
                        book.save()
                        self.stdout.write(self.style.SUCCESS(f'✓ Created borrow record: {student.name} borrowed {book.title}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Demo data setup complete!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin: username=admin, password=admin123')
        self.stdout.write('  Student: username=student1, password=student123')
