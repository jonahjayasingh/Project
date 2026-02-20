from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from doctors.models import Department, Doctor
from patients.models import Patient
from nurses.models import Nurse
from rooms.models import Room, Bed
from pharmacy.models import Medicine
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates initial admin user and sample data'

    def handle(self, *args, **kwargs):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@hospital.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created admin user (username: admin, password: admin123)'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Create Departments
        departments_data = [
            {'name': 'Cardiology', 'description': 'Heart and cardiovascular system'},
            {'name': 'Neurology', 'description': 'Brain and nervous system'},
            {'name': 'Orthopedics', 'description': 'Bones and musculoskeletal system'},
            {'name': 'Pediatrics', 'description': 'Children healthcare'},
            {'name': 'General Medicine', 'description': 'General medical care'},
            {'name': 'Emergency', 'description': 'Emergency medical services'},
        ]
        
        for dept_data in departments_data:
            Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(departments_data)} departments'))

        # Create sample doctor
        if not User.objects.filter(username='doctor1').exists():
            doctor_user = User.objects.create_user(
                username='doctor1',
                email='doctor@hospital.com',
                password='doctor123',
                first_name='John',
                last_name='Smith',
                role='doctor',
                phone='9876543210',
                date_of_birth=date(1980, 5, 15)
            )
            
            cardiology = Department.objects.get(name='Cardiology')
            Doctor.objects.create(
                user=doctor_user,
                department=cardiology,
                specialization='Cardiology',
                qualifications='MBBS, MD (Cardiology)',
                experience_years=10,
                license_number='DOC123456',
                consultation_fee=500,
                available_days='Monday, Wednesday, Friday',
                status='active'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created sample doctor (username: doctor1, password: doctor123)'))

        # Create sample nurse
        if not User.objects.filter(username='nurse1').exists():
            nurse_user = User.objects.create_user(
                username='nurse1',
                email='nurse@hospital.com',
                password='nurse123',
                first_name='Mary',
                last_name='Johnson',
                role='nurse',
                phone='9876543211',
                date_of_birth=date(1990, 8, 20)
            )
            
            cardiology = Department.objects.get(name='Cardiology')
            Nurse.objects.create(
                user=nurse_user,
                department=cardiology,
                qualifications='BSc Nursing',
                license_number='NUR123456',
                shift='morning',
                status='active'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created sample nurse (username: nurse1, password: nurse123)'))

        # Create sample receptionist
        if not User.objects.filter(username='receptionist1').exists():
            User.objects.create_user(
                username='receptionist1',
                email='receptionist@hospital.com',
                password='reception123',
                first_name='Sarah',
                last_name='Williams',
                role='receptionist',
                phone='9876543212',
                date_of_birth=date(1995, 3, 10)
            )
            self.stdout.write(self.style.SUCCESS('✓ Created sample receptionist (username: receptionist1, password: reception123)'))

        # Create sample patient
        if not User.objects.filter(username='patient1').exists():
            patient_user = User.objects.create_user(
                username='patient1',
                email='patient@example.com',
                password='patient123',
                first_name='Robert',
                last_name='Brown',
                role='patient',
                phone='9876543213',
                address='123 Main Street, City',
                date_of_birth=date(1985, 12, 25)
            )
            
            Patient.objects.create(
                user=patient_user,
                blood_group='O+',
                height=175.5,
                weight=70.0,
                emergency_contact_name='Jane Brown',
                emergency_contact_phone='9876543214',
                emergency_contact_relation='Spouse',
                allergies='None',
                chronic_conditions='None',
                status='active'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created sample patient (username: patient1, password: patient123)'))

        # Create Rooms
        room_types = [
            ('101', 'general', 1, 500),
            ('102', 'general', 1, 500),
            ('201', 'private', 2, 1500),
            ('202', 'private', 2, 1500),
            ('301', 'icu', 3, 3000),
            ('302', 'icu', 3, 3000),
        ]
        
        for room_num, room_type, floor, cost in room_types:
            room, created = Room.objects.get_or_create(
                room_number=room_num,
                defaults={
                    'room_type': room_type,
                    'floor': floor,
                    'cost_per_day': cost,
                    'is_active': True
                }
            )
            
            # Create beds for each room
            if created:
                beds_count = 4 if room_type == 'general' else 2 if room_type == 'private' else 1
                for i in range(1, beds_count + 1):
                    Bed.objects.create(
                        room=room,
                        bed_number=f"B{i}",
                        is_occupied=False,
                        is_active=True
                    )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(room_types)} rooms with beds'))

        # Create sample medicines
        medicines_data = [
            ('Paracetamol', 'Acetaminophen', 'tablet', 'PharmaCorp', 100, 5.00),
            ('Amoxicillin', 'Amoxicillin', 'capsule', 'MediLife', 50, 15.00),
            ('Ibuprofen', 'Ibuprofen', 'tablet', 'HealthPlus', 80, 8.00),
            ('Cough Syrup', 'Dextromethorphan', 'syrup', 'PharmaCorp', 30, 50.00),
            ('Aspirin', 'Acetylsalicylic acid', 'tablet', 'MediLife', 120, 3.00),
        ]
        
        for name, generic, category, manufacturer, stock, price in medicines_data:
            Medicine.objects.get_or_create(
                name=name,
                defaults={
                    'generic_name': generic,
                    'category': category,
                    'manufacturer': manufacturer,
                    'stock_quantity': stock,
                    'unit_price': price,
                    'reorder_level': 10,
                    'is_active': True
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(medicines_data)} medicines'))

        self.stdout.write(self.style.SUCCESS('\n=== Setup Complete ==='))
        self.stdout.write(self.style.SUCCESS('You can now login with the following credentials:'))
        self.stdout.write(self.style.SUCCESS('Admin: admin / admin123'))
        self.stdout.write(self.style.SUCCESS('Doctor: doctor1 / doctor123'))
        self.stdout.write(self.style.SUCCESS('Nurse: nurse1 / nurse123'))
        self.stdout.write(self.style.SUCCESS('Receptionist: receptionist1 / reception123'))
        self.stdout.write(self.style.SUCCESS('Patient: patient1 / patient123'))
