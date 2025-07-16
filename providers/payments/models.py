from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator 
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
        validators=[MinValueValidator(0.01)],
        help_text="Amount must be greater than 0.01"
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        db_index=True 
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Additional payment details"
    )
    
    is_completed = models.BooleanField(
        default=False,
        help_text="Mark as true when payment is processed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Provider Payment'
        verbose_name_plural = 'Provider Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['provider']),
            models.Index(fields=['created_at']),
            
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - ${self.amount} - {self.provider_id}"

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None
        super().save(*args, **kwargs)