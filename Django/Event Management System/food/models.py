from django.db import models

class MenuCategory(models.Model):
    name = models.CharField(max_length=50) 
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='food/')
    description = models.TextField(blank=True)
    is_veg = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"
