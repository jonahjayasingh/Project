import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import EventType
from food.models import MenuCategory, MenuItem
from services.models import Service

def seed():
    print("Seeding began...")
    
    # Event Types
    types = [
        ('Marriage', 'https://images.unsplash.com/photo-1519741497674-611481863552?w=800'),
        ('Birthday', 'https://images.unsplash.com/photo-1530103862676-fa8c9d34a689?w=800'),
        ('Puberty', 'https://images.unsplash.com/photo-1510076857177-7470076d4098?w=800'),
    ]
    
    for name, url in types:
        if not EventType.objects.filter(name=name).exists():
            et = EventType(name=name)
            print(f"Created Event Type: {name}")
            et.save()

    # Food Categories
    veg, _ = MenuCategory.objects.get_or_create(name='Veg')
    nonveg, _ = MenuCategory.objects.get_or_create(name='Non-Veg')
    
    # Veg Items
    veg_items = [
        ('Paneer Tikka', 250),
        ('Dal Makhani', 180),
        ('Butter Kulcha', 40),
        ('Veg Pulao', 150),
        ('Gulab Jamun', 80),
    ]
    
    for name, price in veg_items:
        MenuItem.objects.get_or_create(name=name, category=veg, defaults={'price': price, 'is_veg': True})
        
    # Non-Veg Items
    nv_items = [
        ('Chicken Biryani', 300),
        ('Mutton Rogan Josh', 450),
        ('Butter Chicken', 350),
        ('Chicken 65', 200),
    ]
    
    for name, price in nv_items:
        MenuItem.objects.get_or_create(name=name, category=nonveg, defaults={'price': price, 'is_veg': False})

    # Services
    services = [
        ('Photography', 'Candid photography', 15000, 'camera'),
        ('Decoration', 'Floral decoration', 50000, 'flower1'),
        ('Makeup', 'Bridal makeup', 10000, 'brush'),
        ('Car Arrangement', 'Luxury cars', 8000, 'car-front'),
        ('Catering Workers', 'Professional servers', 500, 'people'), 
    ]
    
    for name, desc, price, icon in services:
        Service.objects.get_or_create(
            name=name, 
            defaults={
                'description': desc, 
                'base_price': price, 
                'icon': icon,
                'is_customizable': True,
                'requires_quantity': name == 'Catering Workers'
            }
        )

    print("Seeding completed successfully!")

if __name__ == '__main__':
    seed()
