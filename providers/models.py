from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Provider(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', _('Pendiente')
        APPROVED = 'approved', _('Aprobado')
        REJECTED = 'rejected', _('Rechazado')
        SUSPENDED = 'suspended', _('Suspendido')

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='provider'
    )
    bio = models.TextField(blank=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_completed_services = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    verification_documents = models.JSONField(default=dict, blank=True)
    rejection_reason = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_providers'
    )
    verified_at = models.DateTimeField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
            models.Index(fields=['verification_status']),
        ]

    def __str__(self):
        return f"Provider {self.user.username}"

    @property
    def full_name(self):
        return f"{self.user.profile.firstname} {self.user.profile.lastname}"

    def approve_provider(self, approved_by):
        """Método para aprobar y activar un proveedor"""
        self.verification_status = self.VerificationStatus.APPROVED
        self.is_active = True
        self.verified_by = approved_by
        self.verified_at = timezone.now()
        self.save()
        
        # Actualizar rol de usuario
        self.user.role = 'provider'
        self.user.save()

    def reject_provider(self, reason, rejected_by):
        """Método para rechazar un proveedor"""
        self.verification_status = self.VerificationStatus.REJECTED
        self.is_active = False
        self.rejection_reason = reason
        self.verified_by = rejected_by
        self.verified_at = timezone.now()
        self.save()

    def suspend_provider(self, reason, suspended_by):
        """Método para suspender un proveedor activo"""
        self.verification_status = self.VerificationStatus.SUSPENDED
        self.is_active = False
        self.rejection_reason = reason
        self.verified_by = suspended_by
        self.verified_at = timezone.now()
        self.save()
        
        # Desactivar servicios asociados
        self.services.update(is_active=False)