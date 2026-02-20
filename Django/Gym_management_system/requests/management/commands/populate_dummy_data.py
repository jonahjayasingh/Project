from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from memberships.models import MembershipPlan, MemberMembership
from members.models import Member
from trainers.models import Trainer, TrainerAvailability
from requests.models import MembershipRequest, TrainerRequest
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with dummy data for gym management system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating dummy data...')
        
        # Create Membership Plans
        self.create_membership_plans()
        
        # Create Users (Admin, Trainers, Members)
        admin = self.create_admin()
        trainers = self.create_trainers()
        members = self.create_members()
        
        # Create Trainer Profiles
        trainer_profiles = self.create_trainer_profiles(trainers)
        
        # Create Member Profiles
        member_profiles = self.create_member_profiles(members)
        
        # Create Memberships for members
        self.create_memberships(member_profiles)
        
        # Create Membership Requests
        self.create_membership_requests()
        
        # Create Trainer Requests
        self.create_trainer_requests(member_profiles, trainer_profiles)
        
        self.stdout.write(self.style.SUCCESS('Successfully created dummy data!'))
        self.stdout.write(self.style.SUCCESS('\nLogin Credentials:'))
        self.stdout.write(f'Admin: admin / admin123')
        self.stdout.write(f'Trainer: trainer1 / 12345678')
        self.stdout.write(f'Member: member1 / 12345678')

    def create_membership_plans(self):
        self.stdout.write('Creating membership plans...')
        
        plans_data = [
            {
                'name': 'Basic Monthly',
                'description': 'Perfect for beginners starting their fitness journey',
                'duration_months': 1,
                'price': 1500,
                'access_level': 'gym_only',
                'benefits': 'Access to all gym equipment\nLocker facility\nFree fitness assessment\nBasic workout plan'
            },
            {
                'name': 'Standard Quarterly',
                'description': 'Great value for regular gym-goers',
                'duration_months': 3,
                'price': 4000,
                'access_level': 'gym_classes',
                'benefits': 'All gym equipment access\nUnlimited group classes\nLocker facility\nMonthly fitness assessment\nNutrition guidance'
            },
            {
                'name': 'Premium Semi-Annual',
                'description': 'Comprehensive fitness package',
                'duration_months': 6,
                'price': 7500,
                'access_level': 'premium',
                'benefits': 'All gym equipment\nUnlimited classes\n2 personal training sessions/month\nNutrition consultation\nLocker facility\nFree gym merchandise'
            },
            {
                'name': 'Elite Annual',
                'description': 'Best value for serious fitness enthusiasts',
                'duration_months': 12,
                'price': 15000,
                'access_level': 'premium',
                'benefits': 'All gym equipment\nUnlimited classes\n4 personal training sessions/month\nDedicated nutrition consultant\nPriority class booking\nLocker facility\nFree gym merchandise\nGuest passes (2/month)'
            }
        ]
        
        for plan_data in plans_data:
            MembershipPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(plans_data)} membership plans'))

    def create_admin(self):
        self.stdout.write('Creating admin user...')
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@gym.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        return admin

    def create_trainers(self):
        self.stdout.write('Creating trainer users...')
        trainers = []
        trainer_data = [
            ('John', 'Smith', 'john.smith@gym.com'),
            ('Sarah', 'Johnson', 'sarah.johnson@gym.com'),
            ('Mike', 'Williams', 'mike.williams@gym.com'),
            ('Emma', 'Brown', 'emma.brown@gym.com'),
        ]
        
        for i, (first, last, email) in enumerate(trainer_data, 1):
            trainer, created = User.objects.get_or_create(
                username=f'trainer{i}',
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                    'role': 'trainer',
                    'phone_number': f'+91 98765{i:05d}',
                    'gender': random.choice(['M', 'F'])
                }
            )
            if created:
                trainer.set_password('12345678')
                trainer.save()
            trainers.append(trainer)
        
        return trainers

    def create_members(self):
        self.stdout.write('Creating member users...')
        members = []
        member_data = [
            ('Alice', 'Davis', 'alice.davis@email.com'),
            ('Bob', 'Wilson', 'bob.wilson@email.com'),
            ('Carol', 'Martinez', 'carol.martinez@email.com'),
            ('David', 'Anderson', 'david.anderson@email.com'),
            ('Eve', 'Taylor', 'eve.taylor@email.com'),
            ('Frank', 'Thomas', 'frank.thomas@email.com'),
        ]
        
        for i, (first, last, email) in enumerate(member_data, 1):
            member, created = User.objects.get_or_create(
                username=f'member{i}',
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                    'role': 'member',
                    'phone_number': f'+91 87654{i:05d}',
                    'gender': random.choice(['M', 'F']),
                    'date_of_birth': date(1990 + i, random.randint(1, 12), random.randint(1, 28))
                }
            )
            if created:
                member.set_password('12345678')
                member.save()
            members.append(member)
        
        return members

    def create_trainer_profiles(self, trainers):
        self.stdout.write('Creating trainer profiles...')
        profiles = []
        specializations = ['strength', 'cardio', 'yoga', 'crossfit']
        
        for i, trainer in enumerate(trainers):
            profile, created = Trainer.objects.get_or_create(
                user=trainer,
                defaults={
                    'specialization': specializations[i % len(specializations)],
                    'certifications': f'Certified Personal Trainer\nNutrition Specialist\n{specializations[i % len(specializations)].title()} Expert',
                    'experience_years': random.randint(2, 10),
                    'hourly_rate': random.choice([500, 750, 1000, 1200]),
                    'bio': f'Experienced {specializations[i % len(specializations)]} trainer dedicated to helping clients achieve their fitness goals.',
                    'is_available': True
                }
            )
            profiles.append(profile)
        
        return profiles

    def create_member_profiles(self, members):
        self.stdout.write('Creating member profiles...')
        profiles = []
        blood_groups = ['A+', 'B+', 'O+', 'AB+', 'A-', 'B-']
        
        for member in members:
            profile, created = Member.objects.get_or_create(
                user=member,
                defaults={
                    'emergency_contact_name': f'{member.first_name} Contact',
                    'emergency_contact_phone': f'+91 99999{random.randint(10000, 99999)}',
                    'blood_group': random.choice(blood_groups),
                    'height': random.uniform(150, 190),
                    'weight': random.uniform(50, 100),
                    'fitness_goal': random.choice([
                        'Weight loss',
                        'Muscle gain',
                        'General fitness',
                        'Endurance training'
                    ]),
                    'status': 'active'
                }
            )
            profiles.append(profile)
        
        return profiles

    def create_memberships(self, member_profiles):
        self.stdout.write('Creating active memberships...')
        plans = list(MembershipPlan.objects.all())
        today = timezone.now().date()
        
        for profile in member_profiles[:4]:  # Give first 4 members active memberships
            plan = random.choice(plans)
            MemberMembership.objects.get_or_create(
                member=profile,
                plan=plan,
                defaults={
                    'start_date': today - timedelta(days=random.randint(10, 60)),
                    'end_date': today + timedelta(days=random.randint(30, 180)),
                    'status': 'active',
                    'payment_status': 'paid',
                    'amount_paid': plan.price
                }
            )

    def create_membership_requests(self):
        self.stdout.write('Creating membership requests...')
        plans = list(MembershipPlan.objects.all())
        
        requests_data = [
            {
                'first_name': 'James',
                'last_name': 'Rodriguez',
                'email': 'james.rodriguez@email.com',
                'phone_number': '+91 9876543210',
                'date_of_birth': date(1995, 5, 15),
                'gender': 'M',
                'address': '123 Main Street, Mumbai, Maharashtra 400001',
                'emergency_contact_name': 'Maria Rodriguez',
                'emergency_contact_phone': '+91 9876543211',
                'blood_group': 'O+',
                'height': 175.5,
                'weight': 75.0,
                'fitness_goal': 'Build muscle and improve overall fitness',
                'status': 'pending'
            },
            {
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'email': 'priya.sharma@email.com',
                'phone_number': '+91 9876543212',
                'date_of_birth': date(1992, 8, 20),
                'gender': 'F',
                'address': '456 Park Avenue, Delhi, Delhi 110001',
                'emergency_contact_name': 'Raj Sharma',
                'emergency_contact_phone': '+91 9876543213',
                'blood_group': 'A+',
                'height': 165.0,
                'weight': 60.0,
                'fitness_goal': 'Weight loss and toning',
                'status': 'pending'
            },
            {
                'first_name': 'Robert',
                'last_name': 'Chen',
                'email': 'robert.chen@email.com',
                'phone_number': '+91 9876543214',
                'date_of_birth': date(1988, 3, 10),
                'gender': 'M',
                'address': '789 Lake Road, Bangalore, Karnataka 560001',
                'emergency_contact_name': 'Linda Chen',
                'emergency_contact_phone': '+91 9876543215',
                'blood_group': 'B+',
                'status': 'approved'
            }
        ]
        
        for req_data in requests_data:
            req_data['selected_plan'] = random.choice(plans)
            MembershipRequest.objects.get_or_create(
                email=req_data['email'],
                defaults=req_data
            )

    def create_trainer_requests(self, member_profiles, trainer_profiles):
        self.stdout.write('Creating trainer requests...')
        
        specializations = ['strength', 'cardio', 'yoga', 'general']
        times = ['morning', 'afternoon', 'evening']
        
        for i, profile in enumerate(member_profiles[:3]):  # First 3 members request trainers
            TrainerRequest.objects.get_or_create(
                member=profile,
                defaults={
                    'preferred_specialization': specializations[i % len(specializations)],
                    'preferred_trainer': trainer_profiles[i % len(trainer_profiles)] if i % 2 == 0 else None,
                    'sessions_per_week': random.randint(2, 4),
                    'preferred_time': times[i % len(times)],
                    'fitness_goals': f'I want to improve my {specializations[i % len(specializations)]} training and achieve better results.',
                    'status': random.choice(['pending', 'pending', 'approved'])
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created trainer requests'))
