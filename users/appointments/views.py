from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date, datetime
from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    CreateAppointmentSerializer,
    UpdateAppointmentSerializer,
    UpdateAppointmentStatusSerializer,
    AppointmentDetailSerializer,
    MarkAppointmentAsPaidSerializer
)


# ---------- CONSUMER ----------
class ConsumerAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Appointment.objects.none()
        
        # Solo mostrar appointments no temporales o temporales del usuario
        queryset = Appointment.objects.filter(
            consumer=self.request.user
        ).exclude(
            is_temporary=True,
            payment_completed=False
        )
        
        # Filtros opcionales
        status_filter = self.request.query_params.get('status')
        date_filter = self.request.query_params.get('date')
        include_temporary = self.request.query_params.get('include_temporary', 'false').lower() == 'true'
        
        if include_temporary:
            # Incluir appointments temporales del usuario
            queryset = Appointment.objects.filter(consumer=self.request.user)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date=filter_date)
            except ValueError:
                pass
        
        return queryset.order_by('-appointment_date')


class ConsumerCreateAppointmentView(generics.CreateAPIView):
    serializer_class = CreateAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        service = serializer.validated_data['service']
        provider = service.provider.user
        # Crear appointment como temporal por defecto
        appointment = serializer.save(
            consumer=self.request.user, 
            provider=provider,
            is_temporary=True,
            status=Appointment.Status.TEMPORARY
        )
        
        # Retornar información adicional sobre el appointment temporal
        self.appointment = appointment

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Agregar información sobre expiración
        if hasattr(self, 'appointment'):
            response.data.update({
                'id': self.appointment.id,
                'is_temporary': True,
                'expires_at': self.appointment.expires_at,
                'time_until_expiry': self.appointment.time_until_expiry,
                'message': 'Appointment creado temporalmente. Complete el pago para confirmarlo.'
            })
        
        return response


class ConsumerAppointmentDetailView(generics.RetrieveAPIView):
    """Obtener detalles de un appointment específico"""
    serializer_class = AppointmentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Appointment.objects.none()
        return Appointment.objects.filter(consumer=self.request.user)


class ConsumerUpdateAppointmentView(generics.UpdateAPIView):
    """Editar appointment completo (fecha, hora, notas)"""
    serializer_class = UpdateAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Appointment.objects.none()
        return Appointment.objects.filter(consumer=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # No permitir editar appointments temporales expirados
        if instance.is_temporary and instance.is_expired:
            return Response({
                "error": "No se puede editar un appointment temporal expirado"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "Appointment actualizado correctamente",
            "appointment": AppointmentDetailSerializer(instance).data
        }, status=status.HTTP_200_OK)


class ConsumerCancelAppointmentView(generics.UpdateAPIView):
    serializer_class = UpdateAppointmentStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Appointment.objects.none()
        return Appointment.objects.filter(consumer=self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        
        # Solo permitir cancelar si está pendiente o confirmado
        if obj.status not in [Appointment.Status.PENDING, Appointment.Status.CONFIRMED]:
            return Response({
                "error": "Solo se pueden cancelar citas pendientes o confirmadas"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        obj.status = Appointment.Status.CANCELLED
        obj.notes = request.data.get('notes', obj.notes)
        obj.save()
        
        return Response({
            "message": "Cita cancelada correctamente",
            "status": obj.status
        }, status=status.HTTP_200_OK)


class MarkAppointmentAsPaidView(generics.UpdateAPIView):
    """Marcar appointment como pagado"""
    serializer_class = MarkAppointmentAsPaidSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Appointment.objects.none()
        return Appointment.objects.filter(consumer=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Verificar que sea temporal y no expirado
        if not instance.is_temporary:
            return Response({
                "error": "Solo se pueden marcar como pagados appointments temporales"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if instance.is_expired:
            return Response({
                "error": "No se puede marcar como pagado un appointment temporal expirado"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(
            data=request.data, 
            context={'appointment': instance}
        )
        serializer.is_valid(raise_exception=True)
        
        # Marcar como pagado
        payment_reference = serializer.validated_data.get('payment_reference')
        instance.mark_as_paid(payment_reference)
        
        return Response({
            "message": "Appointment marcado como pagado correctamente",
            "appointment": AppointmentDetailSerializer(instance).data
        }, status=status.HTTP_200_OK)


# ---------- PROVIDER ----------
class ProviderAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Appointment.objects.none()
        
        # Solo mostrar appointments no temporales para providers
        queryset = Appointment.objects.filter(
            provider=self.request.user
        ).exclude(
            is_temporary=True,
            payment_completed=False
        )
        
        # Filtros opcionales
        status_filter = self.request.query_params.get('status')
        date_filter = self.request.query_params.get('date')
        service_filter = self.request.query_params.get('service_id')
        date_range = self.request.query_params.get('date_range')  # today, week, month
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date=filter_date)
            except ValueError:
                pass
        
        if service_filter:
            queryset = queryset.filter(service_id=service_filter)
        
        if date_range:
            today = date.today()
            if date_range == 'today':
                queryset = queryset.filter(appointment_date=today)
            elif date_range == 'week':
                from datetime import timedelta
                week_end = today + timedelta(days=7)
                queryset = queryset.filter(appointment_date__range=[today, week_end])
            elif date_range == 'month':
                from datetime import timedelta
                month_end = today + timedelta(days=30)
                queryset = queryset.filter(appointment_date__range=[today, month_end])
        
        return queryset.order_by('-appointment_date')


class ProviderAppointmentDetailView(generics.RetrieveAPIView):
    """Obtener detalles de un appointment específico para provider"""
    serializer_class = AppointmentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Appointment.objects.none()
        return Appointment.objects.filter(provider=self.request.user)


class ProviderUpdateAppointmentView(generics.UpdateAPIView):
    serializer_class = UpdateAppointmentStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Appointment.objects.none()
        return Appointment.objects.filter(provider=self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', obj.notes)
        
        # Validar transiciones de estado permitidas
        allowed_transitions = {
            Appointment.Status.PENDING: [Appointment.Status.CONFIRMED, Appointment.Status.CANCELLED],
            Appointment.Status.CONFIRMED: [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED],
            Appointment.Status.COMPLETED: [],
            Appointment.Status.CANCELLED: []
        }
        
        current_status = obj.status
        if new_status and new_status not in allowed_transitions.get(current_status, []):
            return Response({
                "error": f"No se puede cambiar de {current_status} a {new_status}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_status:
            obj.status = new_status
        obj.notes = notes
        obj.save()
        
        return Response({
            "message": "Estado de la cita actualizado correctamente",
            "status": obj.status
        }, status=status.HTTP_200_OK)


class ProviderServiceAppointmentsView(generics.ListAPIView):
    """Obtener appointments de un servicio específico del provider"""
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Appointment.objects.none()
        
        service_id = self.kwargs.get('service_id')
        queryset = Appointment.objects.filter(
            provider=self.request.user,
            service_id=service_id
        ).exclude(
            is_temporary=True,
            payment_completed=False
        )
        
        # Filtros opcionales
        status_filter = self.request.query_params.get('status')
        date_filter = self.request.query_params.get('date')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date=filter_date)
            except ValueError:
                pass
        
        return queryset.order_by('-appointment_date')


# ---------- ENDPOINTS GENERALES ----------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def appointment_statistics(request):
    """Obtener estadísticas de appointments del usuario"""
    user = request.user
    
    if user.role == 'consumer':
        appointments = Appointment.objects.filter(consumer=user).exclude(
            is_temporary=True,
            payment_completed=False
        )
    elif user.role == 'provider':
        appointments = Appointment.objects.filter(provider=user).exclude(
            is_temporary=True,
            payment_completed=False
        )
    else:
        return Response({"error": "Rol no válido"}, status=status.HTTP_400_BAD_REQUEST)
    
    total = appointments.count()
    pending = appointments.filter(status=Appointment.Status.PENDING).count()
    confirmed = appointments.filter(status=Appointment.Status.CONFIRMED).count()
    completed = appointments.filter(status=Appointment.Status.COMPLETED).count()
    cancelled = appointments.filter(status=Appointment.Status.CANCELLED).count()
    
    # Estadísticas adicionales para providers
    if user.role == 'provider':
        today_appointments = appointments.filter(appointment_date=date.today()).count()
        upcoming_appointments = appointments.filter(
            appointment_date__gte=date.today(),
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).count()
        
        return Response({
            "total": total,
            "pending": pending,
            "confirmed": confirmed,
            "completed": completed,
            "cancelled": cancelled,
            "today_appointments": today_appointments,
            "upcoming_appointments": upcoming_appointments
        })
    
    return Response({
        "total": total,
        "pending": pending,
        "confirmed": confirmed,
        "completed": completed,
        "cancelled": cancelled
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def provider_dashboard(request):
    """Dashboard específico para providers con información detallada"""
    if request.user.role != 'provider':
        return Response({"error": "Solo para providers"}, status=status.HTTP_403_FORBIDDEN)
    
    # Obtener appointments del provider (excluir temporales no pagados)
    appointments = Appointment.objects.filter(provider=request.user).exclude(
        is_temporary=True,
        payment_completed=False
    )
    
    # Estadísticas por servicio
    from providers.services.models import Service
    provider_services = Service.objects.filter(provider__user=request.user)
    
    service_stats = []
    for service in provider_services:
        service_appointments = appointments.filter(service=service)
        service_stats.append({
            "service_id": service.id,
            "service_title": service.title,
            "total_appointments": service_appointments.count(),
            "pending": service_appointments.filter(status=Appointment.Status.PENDING).count(),
            "confirmed": service_appointments.filter(status=Appointment.Status.CONFIRMED).count(),
            "completed": service_appointments.filter(status=Appointment.Status.COMPLETED).count(),
            "cancelled": service_appointments.filter(status=Appointment.Status.CANCELLED).count(),
        })
    
    # Próximas citas (hoy y mañana)
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    today_appointments = appointments.filter(
        appointment_date=today,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
    ).order_by('appointment_time')
    
    tomorrow_appointments = appointments.filter(
        appointment_date=tomorrow,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
    ).order_by('appointment_time')
    
    return Response({
        "service_statistics": service_stats,
        "today_appointments": AppointmentSerializer(today_appointments, many=True).data,
        "tomorrow_appointments": AppointmentSerializer(tomorrow_appointments, many=True).data,
        "total_appointments": appointments.count(),
        "pending_appointments": appointments.filter(status=Appointment.Status.PENDING).count(),
        "confirmed_appointments": appointments.filter(status=Appointment.Status.CONFIRMED).count(),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_appointment_availability(request):
    """Verificar disponibilidad de horarios para un servicio"""
    service_id = request.GET.get('service_id')
    date = request.GET.get('date')
    
    if not service_id or not date:
        return Response({
            "error": "Se requiere service_id y date"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from providers.services.models import Service
        service = Service.objects.get(id=service_id)
        
        # Simular horarios disponibles (en producción esto sería más complejo)
        available_times = [
            "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"
        ]
        
        # Obtener horarios ocupados para esa fecha (excluir temporales no pagados)
        appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
        occupied_times = Appointment.objects.filter(
            service=service,
            appointment_date=appointment_date,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).exclude(
            is_temporary=True,
            payment_completed=False
        ).values_list('appointment_time', flat=True)
        
        # Convertir a strings para comparación
        occupied_times_str = [time.strftime('%H:%M') for time in occupied_times]
        
        # Filtrar horarios disponibles
        available_times = [time for time in available_times if time not in occupied_times_str]
        
        return Response({
            "service_id": service_id,
            "date": date,
            "available_times": available_times,
            "occupied_times": occupied_times_str
        })
        
    except Service.DoesNotExist:
        return Response({
            "error": "Servicio no encontrado"
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({
            "error": "Formato de fecha inválido. Use YYYY-MM-DD"
        }, status=status.HTTP_400_BAD_REQUEST)
