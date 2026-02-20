from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create a superuser with predefined credentials'

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser(
                username='admin',
                email='admin@gymmanagementsystem.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully!'))
            self.stdout.write(self.style.SUCCESS('Username: admin'))
            self.stdout.write(self.style.SUCCESS('Password: admin123'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists!'))
