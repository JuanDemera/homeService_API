from PIL import Image
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.conf import settings
import os
import uuid
from io import BytesIO

# Excepciones específicas para el servicio de imágenes
class ImageServiceError(Exception):
    """Excepción base para errores del servicio de imágenes"""
    pass

class ImageProcessingError(ImageServiceError):
    """Error al procesar una imagen"""
    pass

class ImageValidationError(ImageServiceError):
    """Error al validar una imagen"""
    pass

class ImageProcessingService:
    """Servicio para procesar y optimizar imágenes"""
    
    @staticmethod
    def resize_image(image_file, max_width=800, max_height=800, quality=85):
        """
        Redimensionar y optimizar una imagen
        
        Args:
            image_file: Archivo de imagen
            max_width: Ancho máximo
            max_height: Alto máximo
            quality: Calidad de compresión (1-100)
        
        Returns:
            BytesIO: Imagen procesada
        """
        try:
            # Abrir la imagen
            img = Image.open(image_file)
            
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calcular nuevas dimensiones manteniendo proporción
            width, height = img.size
            if width > max_width or height > max_height:
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Guardar en buffer
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            return output
            
        except Exception as e:
            raise ImageProcessingError(f"Error al procesar la imagen: {str(e)}")
    
    @staticmethod
    def create_thumbnail(image_file, size=(150, 150)):
        """
        Crear una miniatura de la imagen
        
        Args:
            image_file: Archivo de imagen
            size: Tamaño de la miniatura (ancho, alto)
        
        Returns:
            BytesIO: Miniatura procesada
        """
        try:
            img = Image.open(image_file)
            
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Crear miniatura
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Guardar en buffer
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output
            
        except Exception as e:
            raise ImageProcessingError(f"Error al crear miniatura: {str(e)}")
    
    @staticmethod
    def validate_image_format(image_file):
        """
        Validar el formato de la imagen
        
        Args:
            image_file: Archivo de imagen
        
        Returns:
            bool: True si el formato es válido
        """
        try:
            img = Image.open(image_file)
            return img.format.lower() in ['jpeg', 'jpg', 'png', 'webp']
        except (OSError, IOError, ValueError):
            return False

class ImageStorageService:
    """Servicio para gestionar el almacenamiento de imágenes"""
    
    @staticmethod
    def get_storage_path(model_type, instance_id):
        """
        Generar ruta de almacenamiento para una imagen
        
        Args:
            model_type: Tipo de modelo ('profile', 'service')
            instance_id: ID de la instancia
        
        Returns:
            str: Ruta de almacenamiento
        """
        unique_id = uuid.uuid4().hex[:8]
        return f"{model_type}/{instance_id}/{unique_id}"
    
    @staticmethod
    def cleanup_old_images(model_type, instance_id):
        """
        Limpiar imágenes antiguas
        
        Args:
            model_type: Tipo de modelo
            instance_id: ID de la instancia
        """
        from .models import UserProfileImage, ServiceImage
        
        if model_type == 'profile':
            # Eliminar imagen anterior de perfil
            UserProfileImage.objects.filter(user_id=instance_id).delete()
        elif model_type == 'service':
            # Marcar imágenes no principales como inactivas
            ServiceImage.objects.filter(
                service_id=instance_id,
                is_primary=False
            ).update(is_active=False)
    
    @staticmethod
    def get_image_url(image_field, request=None):
        """
        Obtener URL completa de una imagen
        
        Args:
            image_field: Campo de imagen
            request: Request object para URL absoluta
        
        Returns:
            str: URL de la imagen
        """
        if not image_field:
            return None
        
        if request:
            return request.build_absolute_uri(image_field.url)
        return image_field.url

class ImageValidationService:
    """Servicio para validar imágenes"""
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_PROFILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']
    
    @classmethod
    def validate_profile_image(cls, image_file):
        """
        Validar imagen de perfil
        
        Args:
            image_file: Archivo de imagen
        
        Returns:
            dict: Resultado de validación
        """
        return cls._validate_image(image_file, max_size=cls.MAX_PROFILE_SIZE)
    
    @classmethod
    def validate_service_image(cls, image_file):
        """
        Validar imagen de servicio
        
        Args:
            image_file: Archivo de imagen
        
        Returns:
            dict: Resultado de validación
        """
        return cls._validate_image(image_file, max_size=cls.MAX_FILE_SIZE)
    
    @classmethod
    def _validate_image(cls, image_file, max_size):
        """
        Validación general de imagen
        
        Args:
            image_file: Archivo de imagen
            max_size: Tamaño máximo en bytes
        
        Returns:
            dict: Resultado de validación
        """
        errors = []
        
        # Validar tamaño
        if image_file.size > max_size:
            size_mb = max_size / (1024 * 1024)
            errors.append(f"El archivo es demasiado grande. Máximo {size_mb}MB.")
        
        # Validar extensión
        file_name = image_file.name.lower()
        if not any(file_name.endswith(ext) for ext in cls.ALLOWED_EXTENSIONS):
            errors.append(f"Formato no permitido. Use: {', '.join(cls.ALLOWED_EXTENSIONS)}")
        
        # Validar formato de imagen
        if not ImageProcessingService.validate_image_format(image_file):
            errors.append("El archivo no es una imagen válida.")
        
        # Validar dimensiones
        try:
            img = Image.open(image_file)
            width, height = img.size
            
            if width < 100 or height < 100:
                errors.append("La imagen debe tener al menos 100x100 píxeles.")
            
            if width > 4096 or height > 4096:
                errors.append("La imagen no debe exceder 4096x4096 píxeles.")
                
        except Exception as e:
            errors.append(f"Error al procesar la imagen: {str(e)}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        } 