from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Provider

@receiver(post_save, sender=Provider)
def set_provider_inactive(sender, instance, created, **kwargs):
    if created:
        instance.user.role = 'guest'  # Mantener como guest hasta aprobación
        instance.user.save()