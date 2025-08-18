from rest_framework import permissions
from django.core.exceptions import PermissionDenied

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir que solo los propietarios puedan editar.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permitir lectura para todos los usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Para escritura, verificar que el usuario es el propietario
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'service') and hasattr(obj.service, 'provider'):
            return obj.service.provider.user == request.user
        
        return False

class IsServiceOwner(permissions.BasePermission):
    """
    Permiso para verificar que el usuario es propietario del servicio.
    """
    
    def has_permission(self, request, view):
        # Verificar que el usuario está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Para métodos de lectura, permitir si el usuario está autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Para métodos de escritura, verificar permisos específicos
        return True
    
    def has_object_permission(self, request, view, obj):
        # Verificar que el usuario es propietario del servicio
        if hasattr(obj, 'service') and hasattr(obj.service, 'provider'):
            return obj.service.provider.user == request.user
        elif hasattr(obj, 'provider'):
            return obj.provider.user == request.user
        
        return False

class IsProfileOwner(permissions.BasePermission):
    """
    Permiso para verificar que el usuario es propietario de su perfil.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Solo el propietario puede modificar su imagen de perfil
        return obj.user == request.user

class CanManageServiceImages(permissions.BasePermission):
    """
    Permiso para gestionar imágenes de servicios.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Para métodos de lectura, permitir
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Para métodos de escritura, verificar que el usuario es propietario del servicio
        service_id = view.kwargs.get('service_id')
        if service_id:
            from providers.services.models import Service
            try:
                service = Service.objects.get(id=service_id)
                return service.provider.user == request.user
            except Service.DoesNotExist:
                return False
        
        return True 