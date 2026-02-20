from django.db import models
from django.utils import timezone

class Category(models.Model):
    CATEGORY_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Account(models.Model):
    name = models.CharField(max_length=100)
    initial_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    
    def save(self, *args, **kwargs):
        # Allow updating account balance logic here if needed, or handle via signals/views.
        # For now, simplistic approach or handle in view.
        # But commonly we update balance on save. Let's keep it simple and handle in View/Service for now to avoid side-effect complexity.
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.description} - {self.amount}"

class Budget(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField()

    def __str__(self):
        return f"{self.category.name} - {self.month}"
