from django.db import models
from django.utils import timezone
from datetime import timedelta
from core.models import User
from providers.services.models import Service

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        CONFIRMED = 'confirmed', 'Confirmado'
        CANCELLED = 'cancelled', 'Cancelado'
        COMPLETED = 'completed', 'Completado'
        TEMPORARY = 'temporary', 'Temporal'  # Nuevo estado para appointments no pagados

    consumer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consumer_appointments'
    )
    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='provider_appointments'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TEMPORARY  # Cambiar default a TEMPORARY
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Campos para manejo de appointments temporales
    is_temporary = models.BooleanField(default=True, help_text="Indica si el appointment es temporal (no pagado)")
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha y hora de expiración del appointment temporal"
    )
    payment_completed = models.BooleanField(default=False, help_text="Indica si el pago se completó")
    payment_reference = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Referencia del pago asociado"
    )

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['consumer']),
            models.Index(fields=['provider']),
            models.Index(fields=['status']),
            models.Index(fields=['is_temporary']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Cita #{self.id} - {self.service.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Si es un appointment temporal, establecer expiración (30 minutos)
        if self.is_temporary and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=30)
        
        # Si se marca como pagado, cambiar estado y quitar temporal
        if self.payment_completed and self.is_temporary:
            self.is_temporary = False
            self.status = self.Status.PENDING
            self.expires_at = None
        
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Verificar si el appointment temporal ha expirado"""
        if self.is_temporary and self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def time_until_expiry(self):
        """Tiempo restante hasta la expiración"""
        if self.is_temporary and self.expires_at:
            remaining = self.expires_at - timezone.now()
            if remaining.total_seconds() > 0:
                return remaining
        return None

    def mark_as_paid(self, payment_reference=None):
        """Marcar appointment como pagado"""
        self.payment_completed = True
        self.is_temporary = False
        self.status = self.Status.PENDING
        self.expires_at = None
        if payment_reference:
            self.payment_reference = payment_reference
        self.save()

    def extend_expiry(self, minutes=30):
        """Extender el tiempo de expiración"""
        if self.is_temporary:
            self.expires_at = timezone.now() + timedelta(minutes=minutes)
            self.save()