from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from resorts.models import Resort, Room, Booking
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Clears the database and populates it with initial data.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing database...')
        Booking.objects.all().delete()
        Room.objects.all().delete()
        Resort.objects.all().delete()
        # Delete all non-superuser accounts to start fresh
        User.objects.filter(is_superuser=False).delete()
        
        # --- 1. Manage Admin ---
        try:
            admin = User.objects.get(username='admin')
            admin.set_password('1')
            admin.save()
            self.stdout.write('Admin password reset to "1"')
        except User.DoesNotExist:
            admin = User.objects.create_superuser('admin', 'admin@example.com', '1', role='admin')
            self.stdout.write('Admin user created with password "1"')

        # --- 2. Create Owners ---
        self.stdout.write('Creating owners...')
        owner1 = User.objects.create_user('owner1', 'owner1@example.com', '1', role='owner')
        owner2 = User.objects.create_user('owner2', 'owner2@example.com', '1', role='owner')

        # --- 3. Create Customers ---
        self.stdout.write('Creating customers...')
        customers = []
        for i in range(1, 3):
            customer = User.objects.create_user(f'user{i}', f'user{i}@example.com', '1', role='customer')
            customers.append(customer)
        
        # --- 4. Create Resorts and Rooms ---
        self.stdout.write('Creating resorts and rooms...')
        
        resorts_data = [
            {
                'name': 'Azure Maldives',
                'location': 'Male, Maldives',
                'description': 'Overwater sanctuaries curated for absolute seclusion. Experience the pinnacle of luxury with private pools and direct ocean access.',
                'owner': owner1,
                'is_approved': True,
                'image_url': 'https://images.unsplash.com/photo-1573843981267-be1999ff37cd?auto=format&fit=crop&q=80&w=1974'
            },
            {
                'name': 'Mountain Peak Legacy',
                'location': 'Aspen, USA',
                'description': 'Aspen\'s premier boutique alpine experience. Ski-in/ski-out access with world-class amenities and breathtaking mountain views.',
                'owner': owner1,
                'is_approved': True,
                'image_url': 'https://images.unsplash.com/photo-1519659528534-7fd733a832a0?auto=format&fit=crop&q=80&w=1926'

            },
            {
                'name': 'Urban Oasis',
                'location': 'Tokyo, Japan',
                'description': 'A serene escape in the heart of the bustling city. Traditional Japanese aesthetics meet modern luxury.',
                'owner': owner2,
                'is_approved': True,
                 'image_url': 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&q=80&w=2070'
            },
             {
                'name': 'Hidden Jungle Retreat',
                'location': 'Bali, Indonesia',
                'description': 'Deep in the jungle, find peace and tranquility. A perfect getaway for nature lovers.',
                'owner': owner2,
                'is_approved': False, # Pending approval
                 'image_url': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&q=80&w=2038'
            }
        ]

        for r_data in resorts_data:
            # Pop image_url if not in model, or handle if I add it later. 
            # Looking at model definition, Resort does NOT have image_url. 
            # I will remove it from kwargs before creating.
            # Wait, the user wants dummy data. If the model doesn't support images, I can't add them. 
            # I'll check the model definition again.
            pass

        # Re-reading model definition:
        # class Resort(models.Model):
        #     name = models.CharField(max_length=200)
        #     location = models.CharField(max_length=200)
        #     description = models.TextField()
        #     is_approved = models.BooleanField(default=False)
        #     owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_resorts', null=True, blank=True)
        
        # It does NOT have image_url.
        
        # Correcting the data list to remove image_url
        resorts_data_clean = [
            {
                'name': 'Azure Maldives',
                'location': 'Male, Maldives',
                'description': 'Overwater sanctuaries curated for absolute seclusion. Experience the pinnacle of luxury with private pools and direct ocean access.',
                'owner': owner1,
                'is_approved': True
            },
            {
                'name': 'Mountain Peak Legacy',
                'location': 'Aspen, USA',
                'description': 'Aspen\'s premier boutique alpine experience. Ski-in/ski-out access with world-class amenities and breathtaking mountain views.',
                'owner': owner1,
                'is_approved': True
            },
            {
                'name': 'Urban Oasis',
                'location': 'Tokyo, Japan',
                'description': 'A serene escape in the heart of the bustling city. Traditional Japanese aesthetics meet modern luxury.',
                'owner': owner2,
                'is_approved': True
            },
             {
                'name': 'Hidden Jungle Retreat',
                'location': 'Bali, Indonesia',
                'description': 'Deep in the jungle, find peace and tranquility. A perfect getaway for nature lovers.',
                'owner': owner2,
                'is_approved': False # Pending approval
            }
        ]

        for r_data in resorts_data_clean:
            resort = Resort.objects.create(**r_data)
            
            # Create Rooms for each resort with PRICE = 1
            # Room types: (Type, old_price, capacity, total_rooms)
            room_types = [
                ('Standard', 1, 2, 10), 
                ('Deluxe', 1, 2, 5), 
                ('Suite', 1, 4, 3)
            ]
            
            for r_type, price, cap, total in room_types:
                Room.objects.create(
                    resort=resort,
                    room_type=r_type,
                    capacity=cap,
                    price=price, # SETTING PRICE TO 1
                    total_rooms=total,
                    available_rooms=total # Start full
                )
        
        # --- 5. Export Credentials ---
        with open('a.txt', 'w') as f:
            f.write("--- Credentials (Password is '1' for all) ---\n")
            f.write("Admin: admin\n")
            f.write(f"Owner 1: {owner1.username}\n")
            f.write(f"Owner 2: {owner2.username}\n")
            for user in customers:
                f.write(f"Customer: {user.username}\n")
        
        self.stdout.write(self.style.SUCCESS('Database populated successfully! Credentials saved to a.txt'))
