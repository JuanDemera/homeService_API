from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import UserProfileImage, ServiceImage, ImageUploadLog
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UserProfileImage)
def user_profile_image_saved(sender, instance, created, **kwargs):
    """Señal que se ejecuta cuando se guarda una imagen de perfil"""
    if created:
        logger.info(f"Nueva imagen de perfil creada para usuario {instance.user.username}")
        
        # Limpiar cache relacionado con el usuario
        cache_key = f"user_profile_{instance.user.id}"
        cache.delete(cache_key)

@receiver(post_delete, sender=UserProfileImage)
def user_profile_image_deleted(sender, instance, **kwargs):
    """Señal que se ejecuta cuando se elimina una imagen de perfil"""
    logger.info(f"Imagen de perfil eliminada para usuario {instance.user.username}")
    
    # Limpiar cache relacionado con el usuario
    cache_key = f"user_profile_{instance.user.id}"
    cache.delete(cache_key)

@receiver(post_save, sender=ServiceImage)
def service_image_saved(sender, instance, created, **kwargs):
    """Señal que se ejecuta cuando se guarda una imagen de servicio"""
    if created:
        logger.info(f"Nueva imagen de servicio creada para servicio {instance.service.title}")
        
        # Limpiar cache relacionado con el servicio
        cache_key = f"service_images_{instance.service.id}"
        cache.delete(cache_key)
        
        # Si es la primera imagen, marcarla como principal
        if not ServiceImage.objects.filter(service=instance.service, is_primary=True).exists():
            instance.is_primary = True
            instance.save(update_fields=['is_primary'])
            logger.info(f"Imagen {instance.id} marcada como principal para servicio {instance.service.id}")

@receiver(post_delete, sender=ServiceImage)
def service_image_deleted(sender, instance, **kwargs):
    """Señal que se ejecuta cuando se elimina una imagen de servicio"""
    logger.info(f"Imagen de servicio eliminada: {instance.id}")
    
    # Limpiar cache relacionado con el servicio
    cache_key = f"service_images_{instance.service.id}"
    cache.delete(cache_key)
    
    # Si era la imagen principal, asignar otra como principal
    if instance.is_primary:
        next_primary = ServiceImage.objects.filter(
            service=instance.service,
            is_active=True
        ).exclude(id=instance.id).first()
        
        if next_primary:
            next_primary.is_primary = True
            next_primary.save(update_fields=['is_primary'])
            logger.info(f"Nueva imagen principal asignada: {next_primary.id}")

@receiver(post_save, sender=ImageUploadLog)
def upload_log_saved(sender, instance, created, **kwargs):
    """Señal que se ejecuta cuando se guarda un log de subida"""
    if created:
        log_level = 'INFO' if instance.success else 'ERROR'
        logger.log(
            getattr(logging, log_level),
            f"Log de subida: {instance.upload_type} - {instance.user.username} - {'Éxito' if instance.success else 'Error'}"
        ) 