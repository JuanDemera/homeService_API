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
    ProviderSerializer,
    ProviderProfileSerializer,
    ProviderAdminSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

class ProviderRegisterView(generics.CreateAPIView):
    serializer_class = ProviderRegisterSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = serializer.validated_data.pop('user')
        profile_data = serializer.validated_data.pop('profile')
        documents = serializer.validated_data.pop('documents', {})

        user = User.objects.create_user(
            username=user_data['username'],
            phone=user_data['phone'],
            password=user_data['password'],
            role=User.Role.PROVIDER
        )

        UserProfile.objects.create(
            user=user,
            firstname=profile_data['firstname'],
            lastname=profile_data['lastname'],
            email=profile_data.get('email', f"{user_data['phone']}@temp.com"),
            cedula=profile_data['cedula'],
            birth_date=profile_data.get('birth_date', date(2000, 1, 1))
        )

        provider = Provider.objects.create(
            user=user,
            verification_documents=documents,
            verification_status=Provider.VerificationStatus.PENDING,
            bio=serializer.validated_data.get('bio', "")
        )

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
        
        provider = serializer.save()
        provider.verification_status = Provider.VerificationStatus.PENDING
        provider.save()
        
        return Response({
            "status": "success",
            "message": "Documentos enviados para verificación",
            "verification_status": provider.verification_status
        })

class ProviderVerificationAdminView(generics.UpdateAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderVerificationSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'user__phone'
    lookup_url_kwarg = 'phone'

    def update(self, request, *args, **kwargs):
        provider = self.get_object()
        action = request.data.get('action')
        
        if action == 'approve':
            provider.approve_provider(approved_by=request.user)
            message = "Proveedor aprobado exitosamente"
        elif action == 'reject':
            reason = request.data.get('reason', 'Sin razón especificada')
            provider.reject_provider(reason=reason, rejected_by=request.user)
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
    lookup_field = 'id'

class ProviderListView(generics.ListAPIView):
    serializer_class = ProviderAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Provider.objects.all()

# ✅ Nuevo endpoint para perfil propio
class ProviderProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProviderProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        if not hasattr(self.request.user, 'provider'):
            from django.http import Http404
            raise Http404("Perfil de proveedor no encontrado")
        return self.request.user.provider

# ✅ Endpoint para admin ver perfil por ID
class ProviderDetailAdminView(generics.RetrieveAPIView):
    queryset = Provider.objects.select_related('user__profile')
    serializer_class = ProviderAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'
