from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.db import transaction
from core.models import User
from users.models import UserProfile
from .models import Provider
from datetime import date
from .serializers import (
    ProviderRegisterSerializer,
    ProviderVerificationRequestSerializer,
    ProviderVerificationSerializer,
    ProviderSerializer  # Debes tener este serializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

class ProviderRegisterView(generics.CreateAPIView):
    """
    Registro inicial de proveedores (sin autenticación requerida)
    Campos obligatorios: username, teléfono, cédula, nombres, apellidos
    Campos opcionales: documentos (fotos de cédula)
    """
    serializer_class = ProviderRegisterSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Datos del formulario
        user_data = serializer.validated_data.pop('user')
        profile_data = serializer.validated_data.pop('profile')
        documents = serializer.validated_data.pop('documents', {})

        # Crear usuario
        user = User.objects.create_user(
            username=user_data['username'],
            phone=user_data['phone'],
            password=user_data['password'],
            role=User.Role.PROVIDER
        )

        # Crear perfil
        UserProfile.objects.create(
            user=user,
            firstname=profile_data['firstname'],
            lastname=profile_data['lastname'],
            email=profile_data.get('email', f"{user_data['phone']}@temp.com"),
            cedula=profile_data['cedula'],
            birth_date=profile_data.get('birth_date', date(2000, 1, 1))
        )

        # Crear proveedor
        provider = Provider.objects.create(
            user=user,
            verification_documents=documents,
            verification_status=Provider.VerificationStatus.PENDING,
            bio=serializer.validated_data.get('bio', "")
        )

        # Generar tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "status": "success",
            "user": {
                "username": user.username,
                "phone": user.phone,
                "role": user.role,
                "verification_status": provider.verification_status
            },
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            },
            "message": "Registro exitoso. Complete su verificación para habilitar todas las funciones"
        }, status=status.HTTP_201_CREATED)

class ProviderVerificationRequestView(generics.UpdateAPIView):
    """
    Vista para que el proveedor envíe/actualice sus documentos de verificación
    """
    serializer_class = ProviderVerificationRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.provider

    def update(self, request, *args, **kwargs):
        provider = self.get_object()
        if provider.user != request.user:
            return Response(
                {"error": "No autorizado"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(provider, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Actualizar documentos y cambiar estado a PENDING
        provider = serializer.save()
        provider.verification_status = Provider.VerificationStatus.PENDING
        provider.save()
        
        return Response({
            "status": "success",
            "message": "Documentos enviados para verificación",
            "verification_status": provider.verification_status
        })

class ProviderVerificationAdminView(generics.UpdateAPIView):
    """
    Vista para que el admin apruebe/rechace proveedores
    """
    queryset = Provider.objects.all()
    serializer_class = ProviderVerificationSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'user__phone'

    def update(self, request, *args, **kwargs):
        provider = self.get_object()
        action = request.data.get('action')
        
        if action == 'approve':
            provider.verification_status = Provider.VerificationStatus.APPROVED
            provider.user.role = User.Role.PROVIDER  # Cambiar rol definitivo
            provider.user.save()
            provider.save()
            message = "Proveedor aprobado exitosamente"
        elif action == 'reject':
            provider.verification_status = Provider.VerificationStatus.REJECTED
            provider.rejection_reason = request.data.get('reason', '')
            provider.save()
            message = "Proveedor rechazado"
        else:
            return Response(
                {"error": "Acción no válida"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "status": "success",
            "message": message,
            "verification_status": provider.verification_status
        })

class ProviderUpdateView(generics.UpdateAPIView):
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Provider.objects.all()
    lookup_field = 'id'  # O usa 'pk' si prefieres

class ProviderListView(generics.ListAPIView):
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Provider.objects.all()