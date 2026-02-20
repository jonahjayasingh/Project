from accounts.models import User

# Create Admin User
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='1',
        role='ADMIN'
    )
    print("Admin user created: admin / password123")
else:
    print("Admin user already exists")

# Create Client User
if not User.objects.filter(username='client').exists():
    client = User.objects.create_user(
        username='client',
        email='client@example.com',
        password='1',
        role='CLIENT'
    )
    print("Client user created: client / password123")
else:
    print("Client user already exists")
