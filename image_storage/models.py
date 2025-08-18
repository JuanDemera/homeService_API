from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from providers.services.models import Service
import os
import uuid

User = get_user_model()

def user_profile_image_path(instance, filename):
    """Genera la ruta para las imágenes de perfil de usuarios"""
    ext = filename.split('.')[-1]
    filename = f"profile_{instance.user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    return os.path.join('profiles', filename)

def service_image_path(instance, filename):
    """Genera la ruta para las imágenes de servicios"""
    ext = filename.split('.')[-1]
    filename = f"service_{instance.service_id}_{uuid.uuid4().hex[:8]}.{ext}"
    return os.path.join('services', filename)

class UserProfileImage(models.Model):
    """Modelo para almacenar imágenes de perfil de usuarios"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_image')
    image = models.ImageField(
        upload_to=user_profile_image_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Formatos permitidos: JPG, JPEG, PNG, WEBP"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Imagen de perfil de usuario"
        verbose_name_plural = "Imágenes de perfil de usuarios"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Imagen de perfil de {self.user.username}"
    
    def delete(self, *args, **kwargs):
        # Eliminar el archivo físico cuando se elimina el registro
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
            
            # Limpiar el campo photo en UserProfile
            try:
                from users.models import UserProfile
                user_profile = UserProfile.objects.get(user=self.user)
                user_profile.photo = None
                user_profile.save()
            except UserProfile.DoesNotExist:
                pass  # Si no existe el perfil, no hacer nada
                
        super().delete(*args, **kwargs)

class ServiceImage(models.Model):
    """Modelo para almacenar imágenes de servicios"""
    service_id = models.IntegerField(help_text="ID del servicio")
    image = models.ImageField(
        upload_to=service_image_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Formatos permitidos: JPG, JPEG, PNG, WEBP"
    )
    is_primary = models.BooleanField(default=False, help_text="Indica si es la imagen principal del servicio")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Imagen de servicio"
        verbose_name_plural = "Imágenes de servicios"
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"Imagen de {self.service.name}"
    
    def save(self, *args, **kwargs):
        # Si esta imagen se marca como principal, desmarcar las demás
        if self.is_primary:
            ServiceImage.objects.filter(
                service_id=self.service_id,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Eliminar el archivo físico cuando se elimina el registro
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

class ImageUploadLog(models.Model):
    """Modelo para registrar logs de subida de imágenes"""
    UPLOAD_TYPES = [
        ('profile', 'Imagen de perfil'),
        ('service', 'Imagen de servicio'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_uploads')
    upload_type = models.CharField(max_length=20, choices=UPLOAD_TYPES)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="Tamaño del archivo en bytes")
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de subida de imagen"
        verbose_name_plural = "Logs de subida de imágenes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.upload_type} - {self.user.username} - {self.created_at}"
