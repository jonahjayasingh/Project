from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100) # Makeup, Photography, Decoration, etc.
    description = models.TextField()
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon name")
    is_customizable = models.BooleanField(default=True)
    requires_quantity = models.BooleanField(default=False) 

    def __str__(self):
        return self.name

class ServicePortfolio(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='portfolio')
    image = models.ImageField(upload_to='portfolio/')
    caption = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Portfolio for {self.service.name}"
