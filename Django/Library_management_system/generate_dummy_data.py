"""
Script to generate dummy data for the Library Management System
Run with: python manage.py shell < generate_dummy_data.py
"""

import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from library.models import Student, Book, BorrowRecord

# Clear existing data (except admin)
print("Clearing existing data...")
BorrowRecord.objects.all().delete()
Book.objects.all().delete()
Student.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

print("Generating dummy data...")

# Sample data
FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
    'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley',
    'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle',
    'Kenneth', 'Carol', 'Kevin', 'Amanda', 'Brian', 'Dorothy', 'George', 'Melissa',
    'Edward', 'Deborah', 'Ronald', 'Stephanie', 'Timothy', 'Rebecca', 'Jason', 'Sharon',
    'Jeffrey', 'Laura', 'Ryan', 'Cynthia', 'Jacob', 'Kathleen', 'Gary', 'Amy',
    'Nicholas', 'Shirley', 'Eric', 'Angela', 'Jonathan', 'Helen', 'Stephen', 'Anna',
    'Larry', 'Brenda', 'Justin', 'Pamela', 'Scott', 'Nicole', 'Brandon', 'Emma',
    'Benjamin', 'Samantha', 'Samuel', 'Katherine', 'Raymond', 'Christine', 'Gregory', 'Debra',
    'Alexander', 'Rachel', 'Patrick', 'Catherine', 'Frank', 'Carolyn', 'Jack', 'Janet',
    'Dennis', 'Ruth', 'Jerry', 'Maria', 'Tyler', 'Heather', 'Aaron', 'Diane'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas',
    'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White',
    'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young',
    'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
    'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
    'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
    'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy',
    'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey',
    'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson'
]

DEPARTMENTS = [
    'Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 'Civil Engineering',
    'Business Administration', 'Economics', 'Mathematics', 'Physics', 'Chemistry', 'Biology',
    'English Literature', 'History', 'Psychology', 'Sociology', 'Political Science',
    'Architecture', 'Fine Arts', 'Music', 'Philosophy', 'Law'
]

BOOK_TITLES = [
    'Introduction to Algorithms', 'Clean Code', 'Design Patterns', 'The Pragmatic Programmer',
    'Code Complete', 'Refactoring', 'Head First Design Patterns', 'The Clean Coder',
    'Working Effectively with Legacy Code', 'Domain-Driven Design', 'Patterns of Enterprise Application Architecture',
    'The Mythical Man-Month', 'The Art of Computer Programming', 'Structure and Interpretation of Computer Programs',
    'Compilers: Principles, Techniques, and Tools', 'Operating System Concepts', 'Computer Networks',
    'Database System Concepts', 'Artificial Intelligence: A Modern Approach', 'Machine Learning',
    'Deep Learning', 'Python Crash Course', 'JavaScript: The Good Parts', 'Eloquent JavaScript',
    'You Don\'t Know JS', 'Learning React', 'Node.js Design Patterns', 'Pro Git',
    'The Phoenix Project', 'The DevOps Handbook', 'Site Reliability Engineering',
    'Calculus', 'Linear Algebra', 'Probability and Statistics', 'Discrete Mathematics',
    'Physics for Scientists and Engineers', 'Organic Chemistry', 'General Biology',
    'Principles of Economics', 'Microeconomics', 'Macroeconomics', 'Financial Accounting',
    'Marketing Management', 'Strategic Management', 'Organizational Behavior',
    'To Kill a Mockingbird', 'Pride and Prejudice', '1984', 'The Great Gatsby',
    'Moby Dick', 'War and Peace', 'The Odyssey', 'Hamlet', 'The Catcher in the Rye',
    'Lord of the Flies', 'Animal Farm', 'Brave New World', 'Fahrenheit 451',
    'The Hobbit', 'The Lord of the Rings', 'Harry Potter and the Philosopher\'s Stone',
    'The Chronicles of Narnia', 'A Brief History of Time', 'Sapiens', 'Educated',
    'Thinking, Fast and Slow', 'The Power of Habit', 'Atomic Habits', 'Deep Work',
    'The 7 Habits of Highly Effective People', 'How to Win Friends and Influence People',
    'The Lean Startup', 'Zero to One', 'The Innovator\'s Dilemma', 'Good to Great',
    'The Art of War', 'Meditations', 'The Republic', 'Beyond Good and Evil',
    'The Prince', 'Leviathan', 'The Social Contract', 'On Liberty', 'The Wealth of Nations',
    'Das Kapital', 'The Communist Manifesto', 'The Origin of Species', 'The Selfish Gene',
    'A Short History of Nearly Everything', 'Cosmos', 'The Double Helix', 'The Gene',
    'The Emperor of All Maladies', 'Being Mortal', 'When Breath Becomes Air'
]

AUTHORS = [
    'Thomas H. Cormen', 'Robert C. Martin', 'Erich Gamma', 'Andrew Hunt',
    'Steve McConnell', 'Martin Fowler', 'Eric Freeman', 'Robert C. Martin',
    'Michael Feathers', 'Eric Evans', 'Martin Fowler', 'Frederick P. Brooks',
    'Donald Knuth', 'Harold Abelson', 'Alfred V. Aho', 'Abraham Silberschatz',
    'Andrew S. Tanenbaum', 'Abraham Silberschatz', 'Stuart Russell', 'Tom Mitchell',
    'Ian Goodfellow', 'Eric Matthes', 'Douglas Crockford', 'Marijn Haverbeke',
    'Kyle Simpson', 'Alex Banks', 'Mario Casciaro', 'Scott Chacon',
    'Gene Kim', 'Gene Kim', 'Betsy Beyer', 'James Stewart', 'Gilbert Strang',
    'Sheldon Ross', 'Kenneth Rosen', 'Raymond A. Serway', 'Paula Yurkanis Bruice',
    'Neil Campbell', 'N. Gregory Mankiw', 'Robert Pindyck', 'Olivier Blanchard',
    'Jerry Weygandt', 'Philip Kotler', 'Michael Porter', 'Stephen Robbins',
    'Harper Lee', 'Jane Austen', 'George Orwell', 'F. Scott Fitzgerald',
    'Herman Melville', 'Leo Tolstoy', 'Homer', 'William Shakespeare', 'J.D. Salinger',
    'William Golding', 'George Orwell', 'Aldous Huxley', 'Ray Bradbury',
    'J.R.R. Tolkien', 'J.R.R. Tolkien', 'J.K. Rowling', 'C.S. Lewis',
    'Stephen Hawking', 'Yuval Noah Harari', 'Tara Westover', 'Daniel Kahneman',
    'Charles Duhigg', 'James Clear', 'Cal Newport', 'Stephen Covey', 'Dale Carnegie',
    'Eric Ries', 'Peter Thiel', 'Clayton Christensen', 'Jim Collins',
    'Sun Tzu', 'Marcus Aurelius', 'Plato', 'Friedrich Nietzsche',
    'Niccolò Machiavelli', 'Thomas Hobbes', 'Jean-Jacques Rousseau', 'John Stuart Mill',
    'Adam Smith', 'Karl Marx', 'Karl Marx', 'Charles Darwin', 'Richard Dawkins',
    'Bill Bryson', 'Carl Sagan', 'James Watson', 'Siddhartha Mukherjee',
    'Siddhartha Mukherjee', 'Atul Gawande', 'Paul Kalanithi'
]

CATEGORIES = ['fiction', 'non_fiction', 'science', 'technology', 'history', 'biography', 'children', 'reference', 'other']

# Generate 150 students
print("Creating students...")
students = []
for i in range(150):
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    username = f"{first_name.lower()}{last_name.lower()}{i}"
    email = f"{username}@university.edu"
    
    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password='student123'
    )
    
    # Create student profile
    student = Student.objects.create(
        user=user,
        name=f"{first_name} {last_name}",
        email=email,
        department=random.choice(DEPARTMENTS),
        class_name=f"{random.choice(['CS', 'EE', 'ME', 'BA', 'MATH', 'PHYS'])}-{random.randint(101, 499)}",
        max_books_allowed=random.choice([3, 3, 3, 4, 5])  # Most get 3
    )
    students.append(student)

print(f"Created {len(students)} students")

# Generate 200 books
print("Creating books...")
books = []
for i in range(min(len(BOOK_TITLES), 200)):
    title = BOOK_TITLES[i % len(BOOK_TITLES)]
    author = AUTHORS[i % len(AUTHORS)]
    
    total_copies = random.randint(2, 10)
    
    book = Book.objects.create(
        title=f"{title}" if i < len(BOOK_TITLES) else f"{title} - Volume {i // len(BOOK_TITLES) + 1}",
        author=author,
        isbn=f"978{random.randint(1000000000, 9999999999)}",
        category=random.choice(CATEGORIES),
        total_copies=total_copies,
        available_copies=total_copies,
        description=f"A comprehensive guide to {title.lower()}. Essential reading for students and professionals alike."
    )
    books.append(book)

print(f"Created {len(books)} books")

# Generate borrow records with various statuses
print("Creating borrow records...")

now = timezone.now()
records_created = 0

# Create 50 pending requests
for _ in range(50):
    student = random.choice(students)
    book = random.choice(books)
    
    # Check if student already has this book
    existing = BorrowRecord.objects.filter(
        student=student,
        book=book,
        status__in=['pending', 'approved', 'borrowed', 'overdue']
    ).exists()
    
    if not existing:
        request_date = now - timedelta(days=random.randint(0, 5))
        BorrowRecord.objects.create(
            student=student,
            book=book,
            request_date=request_date,
            requested_days=random.choice([7, 14, 21, 30]),
            notes=random.choice(['', '', '', 'Need for exam preparation', 'Required for project', 'Research purposes']),
            status='pending'
        )
        records_created += 1

# Create 30 approved requests (ready for collection)
for _ in range(30):
    student = random.choice(students)
    book = random.choice(books)
    
    existing = BorrowRecord.objects.filter(
        student=student,
        book=book,
        status__in=['pending', 'approved', 'borrowed', 'overdue']
    ).exists()
    
    if not existing:
        request_date = now - timedelta(days=random.randint(1, 7))
        approved_date = request_date + timedelta(hours=random.randint(2, 48))
        requested_days = random.choice([7, 14, 21, 30])
        
        BorrowRecord.objects.create(
            student=student,
            book=book,
            request_date=request_date,
            requested_days=requested_days,
            approved_date=approved_date,
            approved_by=User.objects.filter(is_superuser=True).first(),
            due_date=(approved_date + timedelta(days=requested_days)).date(),
            status='approved'
        )
        records_created += 1

# Create 100 currently borrowed books
for _ in range(100):
    student = random.choice(students)
    book = random.choice(books)
    
    existing = BorrowRecord.objects.filter(
        student=student,
        book=book,
        status__in=['pending', 'approved', 'borrowed', 'overdue']
    ).exists()
    
    if not existing and book.available_copies > 0:
        request_date = now - timedelta(days=random.randint(7, 30))
        approved_date = request_date + timedelta(hours=random.randint(2, 48))
        requested_days = random.choice([7, 14, 21, 30])
        borrow_date = approved_date + timedelta(days=random.randint(0, 3))
        due_date = (borrow_date + timedelta(days=requested_days)).date()
        
        BorrowRecord.objects.create(
            student=student,
            book=book,
            request_date=request_date,
            requested_days=requested_days,
            approved_date=approved_date,
            approved_by=User.objects.filter(is_superuser=True).first(),
            borrow_date=borrow_date,
            due_date=due_date,
            status='borrowed'
        )
        
        # Update available copies
        book.available_copies -= 1
        book.save()
        records_created += 1

# Create 20 overdue books
for _ in range(20):
    student = random.choice(students)
    book = random.choice(books)
    
    existing = BorrowRecord.objects.filter(
        student=student,
        book=book,
        status__in=['pending', 'approved', 'borrowed', 'overdue']
    ).exists()
    
    if not existing and book.available_copies > 0:
        request_date = now - timedelta(days=random.randint(30, 60))
        approved_date = request_date + timedelta(hours=random.randint(2, 48))
        requested_days = random.choice([7, 14, 21])
        borrow_date = approved_date + timedelta(days=random.randint(0, 3))
        due_date = (borrow_date + timedelta(days=requested_days)).date()
        
        BorrowRecord.objects.create(
            student=student,
            book=book,
            request_date=request_date,
            requested_days=requested_days,
            approved_date=approved_date,
            approved_by=User.objects.filter(is_superuser=True).first(),
            borrow_date=borrow_date,
            due_date=due_date,
            status='overdue'
        )
        
        # Update available copies
        book.available_copies -= 1
        book.save()
        records_created += 1

# Create 150 returned books (history)
for _ in range(150):
    student = random.choice(students)
    book = random.choice(books)
    
    request_date = now - timedelta(days=random.randint(30, 180))
    approved_date = request_date + timedelta(hours=random.randint(2, 48))
    requested_days = random.choice([7, 14, 21, 30])
    borrow_date = approved_date + timedelta(days=random.randint(0, 3))
    due_date = (borrow_date + timedelta(days=requested_days)).date()
    return_date = borrow_date + timedelta(days=random.randint(1, requested_days + 5))
    
    BorrowRecord.objects.create(
        student=student,
        book=book,
        request_date=request_date,
        requested_days=requested_days,
        approved_date=approved_date,
        approved_by=User.objects.filter(is_superuser=True).first(),
        borrow_date=borrow_date,
        due_date=due_date,
        return_date=return_date,
        status='returned'
    )
    records_created += 1

# Create 20 rejected requests
for _ in range(20):
    student = random.choice(students)
    book = random.choice(books)
    
    request_date = now - timedelta(days=random.randint(1, 30))
    
    BorrowRecord.objects.create(
        student=student,
        book=book,
        request_date=request_date,
        requested_days=random.choice([7, 14, 21, 30]),
        notes=random.choice(['', 'Need urgently', 'For assignment']),
        admin_notes=random.choice(['Book reserved for another student', 'Not available for this period', 'Student has overdue books']),
        status='rejected'
    )
    records_created += 1

print(f"Created {records_created} borrow records")

# Print summary
print("\n" + "="*50)
print("DUMMY DATA GENERATION COMPLETE!")
print("="*50)
print(f"Total Students: {Student.objects.count()}")
print(f"Total Books: {Book.objects.count()}")
print(f"Total Borrow Records: {BorrowRecord.objects.count()}")
print("\nBorrow Records by Status:")
print(f"  Pending: {BorrowRecord.objects.filter(status='pending').count()}")
print(f"  Approved: {BorrowRecord.objects.filter(status='approved').count()}")
print(f"  Borrowed: {BorrowRecord.objects.filter(status='borrowed').count()}")
print(f"  Overdue: {BorrowRecord.objects.filter(status='overdue').count()}")
print(f"  Returned: {BorrowRecord.objects.filter(status='returned').count()}")
print(f"  Rejected: {BorrowRecord.objects.filter(status='rejected').count()}")
print("\nYou can now test the system with realistic data!")
print("="*50)
