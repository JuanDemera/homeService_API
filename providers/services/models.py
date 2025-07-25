from django.db import models
from providers.models import Provider
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Service(models.Model):
    provider = models.ForeignKey(
        Provider, 
        on_delete=models.CASCADE, 
        related_name='services'
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT,
        related_name='services'
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    duration_minutes = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    photo = models.URLField(max_length=300, blank=True, null=True)  # <--- Nuevo campo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        indexes = [
            models.Index(fields=['provider']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.provider.user.username}"