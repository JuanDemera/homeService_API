from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    CreateAppointmentSerializer,
    UpdateAppointmentStatusSerializer
)


# ---------- CONSUMER ----------
class ConsumerAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(consumer=self.request.user).order_by('-appointment_date')


class ConsumerCreateAppointmentView(generics.CreateAPIView):
    serializer_class = CreateAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        service = serializer.validated_data['service']
        provider = service.provider.user
        serializer.save(consumer=self.request.user, provider=provider)


class ConsumerCancelAppointmentView(generics.UpdateAPIView):
    serializer_class = UpdateAppointmentStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        if obj.consumer != self.request.user:
            raise PermissionDenied("No puede modificar esta cita")
        return obj

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = Appointment.Status.CANCELLED
        obj.notes = request.data.get('notes', obj.notes)
        obj.save()
        return Response({
            "message": "Cita cancelada correctamente",
            "status": obj.status
        }, status=status.HTTP_200_OK)


# ---------- PROVIDER ----------
class ProviderAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(provider=self.request.user).order_by('-appointment_date')


class ProviderUpdateAppointmentView(generics.UpdateAPIView):
    serializer_class = UpdateAppointmentStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        if obj.provider != self.request.user:
            raise PermissionDenied("No puede modificar esta cita")
        return obj
