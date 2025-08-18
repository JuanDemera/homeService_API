from rest_framework import serializers
from .models import UserProfileImage, ServiceImage, ImageUploadLog
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from PIL import Image
import os

User = get_user_model()

class UserProfileImageSerializer(serializers.ModelSerializer):
    """Serializer para imágenes de perfil de usuarios"""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    image_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfileImage
        fields = ['id', 'user', 'image', 'image_url', 'file_size', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj and obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_file_size(self, obj):
        if obj and obj.image and hasattr(obj.image, 'size'):
            return obj.image.size
        return 0
    
    def validate_image(self, value):
        """Validar la imagen antes de guardarla"""
        if value:
            # Verificar el tamaño del archivo (máximo 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("El archivo es demasiado grande. El tamaño máximo es 5MB.")
            
            # Verificar las dimensiones de la imagen
            try:
                img = Image.open(value)
                width, height = img.size
                
                # Dimensiones mínimas
                if width < 100 or height < 100:
                    raise serializers.ValidationError("La imagen debe tener al menos 100x100 píxeles.")
                
                # Dimensiones máximas
                if width > 2048 or height > 2048:
                    raise serializers.ValidationError("La imagen no debe exceder 2048x2048 píxeles.")
                
            except Exception as e:
                raise serializers.ValidationError(f"Error al procesar la imagen: {str(e)}")
        
        return value
    
    def create(self, validated_data):
        """Crear o actualizar la imagen de perfil"""
        user = self.context['request'].user
        
        # Obtener o crear la instancia de imagen de perfil
        instance, created = UserProfileImage.objects.get_or_create(user=user)
        
        # Si ya existe una imagen, eliminar el archivo anterior
        if not created and instance.image:
            try:
                if os.path.isfile(instance.image.path):
                    os.remove(instance.image.path)
            except Exception:
                pass  # Ignorar errores al eliminar archivo
        
        # Actualizar con la nueva imagen
        instance.image = validated_data['image']
        instance.save()
        
        # Actualizar el campo photo en UserProfile
        try:
            from users.models import UserProfile
            user_profile = UserProfile.objects.get(user=user)
            request = self.context.get('request')
            if request:
                # Construir URL absoluta
                photo_url = request.build_absolute_uri(instance.image.url)
            else:
                photo_url = instance.image.url
            user_profile.photo = photo_url
            user_profile.save()
        except UserProfile.DoesNotExist:
            pass  # Si no existe el perfil, no hacer nada
        
        # Registrar en el log
        ImageUploadLog.objects.create(
            user=user,
            upload_type='profile',
            file_name=os.path.basename(instance.image.name),
            file_size=instance.image.size,
            success=True
        )
        
        return instance
    
    def update(self, instance, validated_data):
        """Actualizar la imagen de perfil"""
        # Si se proporciona una nueva imagen
        if 'image' in validated_data:
            # Eliminar el archivo anterior si existe
            if instance.image:
                try:
                    if os.path.isfile(instance.image.path):
                        os.remove(instance.image.path)
                except Exception:
                    pass  # Ignorar errores al eliminar archivo
            
            # Actualizar con la nueva imagen
            instance.image = validated_data['image']
            instance.save()
            
            # Actualizar el campo photo en UserProfile
            try:
                from users.models import UserProfile
                user_profile = UserProfile.objects.get(user=instance.user)
                request = self.context.get('request')
                if request:
                    # Construir URL absoluta
                    photo_url = request.build_absolute_uri(instance.image.url)
                else:
                    photo_url = instance.image.url
                user_profile.photo = photo_url
                user_profile.save()
            except UserProfile.DoesNotExist:
                pass  # Si no existe el perfil, no hacer nada
            
            # Registrar en el log
            user = self.context['request'].user
            ImageUploadLog.objects.create(
                user=user,
                upload_type='profile',
                file_name=os.path.basename(instance.image.name),
                file_size=instance.image.size,
                success=True
            )
        
        return instance

class ServiceImageSerializer(serializers.ModelSerializer):
    """Serializer para imágenes de servicios"""
    service = serializers.PrimaryKeyRelatedField(read_only=True)
    image_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceImage
        fields = ['id', 'service', 'image', 'image_url', 'file_size', 'is_primary', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'service', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj and obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_file_size(self, obj):
        if obj and obj.image and hasattr(obj.image, 'size'):
            return obj.image.size
        return 0
    
    def validate_image(self, value):
        """Validar la imagen antes de guardarla"""
        if value:
            # Verificar el tamaño del archivo (máximo 10MB para servicios)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("El archivo es demasiado grande. El tamaño máximo es 10MB.")
            
            # Verificar las dimensiones de la imagen
            try:
                img = Image.open(value)
                width, height = img.size
                
                # Dimensiones mínimas
                if width < 200 or height < 200:
                    raise serializers.ValidationError("La imagen debe tener al menos 200x200 píxeles.")
                
                # Dimensiones máximas
                if width > 4096 or height > 4096:
                    raise serializers.ValidationError("La imagen no debe exceder 4096x4096 píxeles.")
                
            except Exception as e:
                raise serializers.ValidationError(f"Error al procesar la imagen: {str(e)}")
        
        return value
    
    def create(self, validated_data):
        """Crear nueva imagen de servicio"""
        service_id = self.context.get('service_id')
        if not service_id:
            raise serializers.ValidationError("Se requiere el ID del servicio.")
        
        from providers.services.models import Service
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            raise serializers.ValidationError("El servicio especificado no existe.")
        
        validated_data['service'] = service
        instance = super().create(validated_data)
        
        # Registrar en el log
        user = self.context['request'].user
        ImageUploadLog.objects.create(
            user=user,
            upload_type='service',
            file_name=os.path.basename(instance.image.name),
            file_size=instance.image.size,
            success=True
        )
        
        return instance

class ImageUploadLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de subida de imágenes"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    upload_type_display = serializers.CharField(source='get_upload_type_display', read_only=True)
    
    class Meta:
        model = ImageUploadLog
        fields = ['id', 'user', 'user_username', 'upload_type', 'upload_type_display', 
                 'file_name', 'file_size', 'success', 'error_message', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class BulkImageUploadSerializer(serializers.Serializer):
    """Serializer para subida múltiple de imágenes de servicios"""
    images = serializers.ListField(
        child=serializers.ImageField(),
        max_length=10,
        help_text="Máximo 10 imágenes por subida"
    )
    service_id = serializers.IntegerField()
    
    def validate_images(self, value):
        """Validar la lista de imágenes"""
        if not value:
            raise serializers.ValidationError("Debe proporcionar al menos una imagen.")
        
        if len(value) > 10:
            raise serializers.ValidationError("No puede subir más de 10 imágenes a la vez.")
        
        # Validar cada imagen
        for image in value:
            if image.size > 10 * 1024 * 1024:
                raise serializers.ValidationError(f"La imagen {image.name} es demasiado grande. Máximo 10MB.")
        
        return value
    
    def validate_service_id(self, value):
        """Validar que el servicio existe"""
        from providers.services.models import Service
        try:
            Service.objects.get(id=value)
        except Service.DoesNotExist:
            raise serializers.ValidationError("El servicio especificado no existe.")
        return value 