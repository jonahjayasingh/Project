#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gym_management_system.settings')
django.setup()

from django.core.management import call_command

print("Populating database with dummy data...")
call_command('populate_dummy_data')
print("\nDone! You can now login with:")
print("Admin: admin / 12345678")
print("Trainer: trainer1 / 12345678")
print("Member: member1 / 12345678")
