from django.core.management.base import BaseCommand
from transactions.models import Category, Account, Transaction
from django.utils import timezone
import random
from datetime import timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populates the database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating data...')

        # Create Categories
        income_cats = ['Salary', 'Freelance', 'Investments', 'Gifts']
        expense_cats = ['Food', 'Rent', 'Utilities', 'Transportation', 'Entertainment', 'Shopping', 'Health', 'Education']
        
        categories = []
        for name in income_cats:
            cat, created = Category.objects.get_or_create(name=name, type='INCOME')
            categories.append(cat)
            
        for name in expense_cats:
            cat, created = Category.objects.get_or_create(name=name, type='EXPENSE')
            categories.append(cat)

        self.stdout.write(f'Created {len(categories)} categories.')

        # Create Accounts
        account_data = [
            {'name': 'Main Bank Account', 'initial_balance': 5000},
            {'name': 'Cash Wallet', 'initial_balance': 200},
            {'name': 'Savings', 'initial_balance': 10000},
            {'name': 'Credit Card', 'initial_balance': 0},
        ]
        
        accounts = []
        for acc_data in account_data:
            acc, created = Account.objects.get_or_create(name=acc_data['name'], defaults={'initial_balance': acc_data['initial_balance'], 'current_balance': acc_data['initial_balance']})
            if created:
                # Ensure current balance matches initial if just created (though default is handled, being explicit is safe)
                acc.current_balance = acc_data['initial_balance']
                acc.save()
            accounts.append(acc)

        self.stdout.write(f'Created {len(accounts)} accounts.')

        # Generate Transactions
        # Clear existing transactions to avoid dupes/mess if run multiple times? 
        # User asked to "add", so I'll just add. But to keep balances sane, maybe better to clear?
        # Let's just add new ones.
        
        start_date = timezone.now().date() - timedelta(days=180) # Last 6 months
        
        for _ in range(50):
            date = start_date + timedelta(days=random.randint(0, 180))
            is_income = random.choice([True, False, False, False]) # 25% chance of income
            
            if is_income:
                cat = random.choice([c for c in categories if c.type == 'INCOME'])
                amount = random.randint(1000, 5000)
                desc = f"Income from {cat.name}"
                type = 'INCOME'
            else:
                cat = random.choice([c for c in categories if c.type == 'EXPENSE'])
                amount = random.randint(10, 200)
                desc = f"Spent on {cat.name}"
                type = 'EXPENSE'
                
            account = random.choice(accounts)
            
            Transaction.objects.create(
                description=desc,
                amount=amount,
                date=date,
                category=cat,
                account=account,
                type=type
            )
            
            # Update Account Balance
            if type == 'INCOME':
                account.current_balance += Decimal(amount)
            else:
                account.current_balance -= Decimal(amount)
            account.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated dummy data!'))
