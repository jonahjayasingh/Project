import random
from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
from app.models import  UserPermission
from student.models import StudentDetails


class Command(BaseCommand):
    help = 'Generates fake student data for testing with proper branches and semesters'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of fake students to create')

    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']
        
        # Degree programs
        degree_programs = {
            'BE': ['Computer Science', 'Electrical', 'Mechanical', 'Civil', 'Electronics'],
            'BTech': ['Computer Science', 'Information Technology', 'Biotechnology', 'Chemical'],
            'BSc': ['Physics', 'Chemistry', 'Mathematics', 'Computer Science'],
            'BCom': ['General', 'Accounting', 'Finance'],
            'BA': ['English', 'History', 'Economics']
        }
        
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for i in range(count):
            try:
                # Create user
                username = f"student{fake.unique.user_name()}"
                email = fake.unique.email()
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='testpass123'
                )
                
                # Create UserPermission
                UserPermission.objects.create(
                    user=user,
                    is_student=True,
                    is_approved=True,
                    is_teacher=False,
                    is_company=False,
                    is_principal=False
                )
                
                # Select random degree and specialization
                degree = random.choice(list(degree_programs.keys()))
                specialization = random.choice(degree_programs[degree])
                
                # Determine year and semester (1-8)
                semester = random.randint(1, 8)
                year = ((semester - 1) // 2) + 1  # Calculate year from semester
                
                # Create StudentDetails
                StudentDetails.objects.create(
                    user=user,
                    name=fake.name(),
                    email=email,
                    phone=fake.unique.phone_number()[:15],
                    address=fake.address(),
                    date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=25),
                    gender=random.choice(['M', 'F', 'O']),
                    blood_group=random.choice(blood_groups),
                    profile_picture=None,
                    course=degree,
                    branch=specialization,  # Using degree as branch (BE, BTech, etc.)
                    year=str(year),
                    sem=str(semester),
                    roll_no=f"{degree[:2]}{fake.unique.random_number(digits=4)}",
                    reg_no=f"REG{fake.unique.random_number(digits=8)}",
                    cgpa=round(random.uniform(5.0, 10.0), 2)
                )
                
                self.stdout.write(self.style.SUCCESS(f'Created {degree} student {i+1}/{count} (Semester {semester})'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating student: {e}'))
                continue

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} fake students!'))