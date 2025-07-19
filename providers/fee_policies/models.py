from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from providers.services.models import Category
from django.core.exceptions import ValidationError

class FeePolicy(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='fee_policies'
    )
    fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_fee_policies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Fee Policy'
        verbose_name_plural = 'Fee Policies'
        ordering = ['-valid_from']
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'valid_from'],
                name='unique_category_valid_from'
            )
        ]

    def __str__(self):
        return f"Comisión {self.fee_percentage}% para {self.category.name} desde {self.valid_from}"

    def clean(self):
        if self.valid_to and self.valid_to < self.valid_from:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")
        
        # Verificar superposición con otras políticas
        overlapping_policies = FeePolicy.objects.filter(
            category=self.category,
            valid_from__lte=self.valid_to if self.valid_to else self.valid_from,
            valid_to__gte=self.valid_from,
            is_active=True
        ).exclude(pk=self.pk if self.pk else None)
        
        if overlapping_policies.exists():
            raise ValidationError("Existe una política activa que se superpone con este período")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)