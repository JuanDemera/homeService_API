from django.db import models
from core.models import User
from providers.services.models import Service

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        CONFIRMED = 'confirmed', 'Confirmado'
        CANCELLED = 'cancelled', 'Cancelado'
        COMPLETED = 'completed', 'Completado'

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
        default=Status.PENDING
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['consumer']),
            models.Index(fields=['provider']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Cita #{self.id} - {self.service.title} ({self.get_status_display()})"