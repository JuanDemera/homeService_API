from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Provider
from .serializers import (
    ProviderSerializer,
    ProviderRegisterSerializer,
    ProviderVerificationSerializer
)

class ProviderDetailView(generics.RetrieveAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user__username'

class ProviderRegisterView(generics.CreateAPIView):
    serializer_class = ProviderRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'guest':
            raise PermissionDenied("Only guest users can register as providers")
        serializer.save()

class ProviderVerificationView(generics.UpdateAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderVerificationSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'user__username'

    def perform_update(self, serializer):
        provider = serializer.save()
        action = self.request.data.get('action')
        
        if action == 'approve':
            provider.approve_provider(self.request.user)
        elif action == 'reject':
            provider.reject_provider(
                reason=self.request.data.get('rejection_reason'),
                rejected_by=self.request.user
            )
        elif action == 'suspend':
            provider.suspend_provider(
                reason=self.request.data.get('rejection_reason'),
                suspended_by=self.request.user
            )

class ProviderAvailabilityView(generics.UpdateAPIView):
    """Vista para activar/desactivar disponibilidad"""
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'user__username'

    def patch(self, request, *args, **kwargs):
        provider = self.get_object()
        is_active = request.data.get('is_active', False)
        
        if not provider.verification_status == Provider.VerificationStatus.APPROVED:
            return Response(
                {'error': 'El proveedor debe estar aprobado para cambiar disponibilidad'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        provider.is_active = is_active
        provider.save()
        
        return Response(
            {'status': f'Disponibilidad {"activada" if is_active else "desactivada"} correctamente'},
            status=status.HTTP_200_OK
        )