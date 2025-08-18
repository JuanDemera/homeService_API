from rest_framework import permissions

class IsAddressOwner(permissions.BasePermission):
    """
    Permiso para permitir solo a los propietarios de la dirección gestionarla.
    """
    message = "No tienes permisos para gestionar esta dirección."

    def has_object_permission(self, request, view, obj):
        # Verificar que el usuario es el propietario de la dirección
        return obj.user == request.user

class CanManageAddresses(permissions.BasePermission):
    """
    Permiso para gestionar direcciones (solo consumers y providers).
    """
    message = "Solo los usuarios consumer y provider pueden gestionar direcciones."

    def has_permission(self, request, view):
        # Solo permitir a consumers y providers
        return request.user.role in ['consumer', 'provider'] 