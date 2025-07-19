from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from core.models import User

class CustomJWTAuthentication(JWTAuthentication):
    """
    Autenticación JWT personalizada con:
    - Validación de usuario activo
    - Control de cuentas suspendidas
    - Protección contra tokens inválidos
    - Actualización de último login
    """
    
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('user_id')
            user = User.objects.select_related('profile').get(pk=user_id)
            
            # Verificar si el usuario está activo
            if not user.is_active:
                raise exceptions.AuthenticationFailed(
                    _('Account disabled, contact support'),
                    code='account_disabled'
                )
                
            # Verificar si la cuenta está suspendida
            if user.disabled:
                raise exceptions.AuthenticationFailed(
                    _('Account suspended: ') + (user.disabled_reason or _('No reason provided')),
                    code='account_suspended'
                )
            
            # Verificar si el token fue emitido antes del último login
            if user.last_login and validated_token.get('iat') < int(user.last_login.timestamp()):
                raise exceptions.AuthenticationFailed(
                    _('Invalid token. Please login again.'),
                    code='token_invalid'
                )
            
            # Actualizar último login (sin guardar aún)
            user.last_login = timezone.now()
            
            return user
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _('User not found'),
                code='user_not_found'
            )
        except Exception as e:
            raise exceptions.AuthenticationFailed(
                _('Authentication failed'),
                code='authentication_failed'
            )

    def authenticate(self, request):
        """
        Sobrescribe el método authenticate para incluir el user en el request
        después de la validación exitosa
        """
        try:
            auth_result = super().authenticate(request)
            if auth_result is None:
                return None
                
            user, token = auth_result
            user.save()  # Guarda el último login
            
            # Cachear datos del usuario para requests posteriores
            cache_key = f"user_{user.id}_data"
            cache.set(cache_key, {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'is_verified': user.is_verified
            }, timeout=300)  # 5 minutos
            
            return (user, token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(
                _('Error during authentication'),
                code='authentication_error'
            )