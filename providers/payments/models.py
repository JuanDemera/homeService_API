from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import User

class ProviderPayment(models.Model):
    class TransactionType(models.TextChoices):
        PAYOUT = 'payout', 'Payout'
        FEE = 'fee', 'Fee'
        ADJUSTMENT = 'adjustment', 'Adjustment'

    provider = models.ForeignKey(
        'providers.Provider',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['provider']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - ${self.amount}"

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)