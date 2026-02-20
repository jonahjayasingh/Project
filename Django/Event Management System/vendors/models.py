from django.db import models

class Vendor(models.Model):
    """
    Vendor model for managing event service providers.
    Only admins can manage vendors.
    """
    CATEGORY_CHOICES = [
        ('Caterer', 'Caterer'),
        ('Decorator', 'Decorator'),
        ('Photographer', 'Photographer'),
    ]
    
    name = models.CharField(max_length=200, help_text='Vendor name')
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text='Vendor service category'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Vendor service price'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.category} (Rs. {self.price})"
