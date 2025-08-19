from rest_framework import serializers
from django.utils import timezone
from datetime import date, datetime
from .models import Appointment
from providers.services.serializers import ProviderServiceSerializer
from core.serializers import UserSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    service = ProviderServiceSerializer(read_only=True)
    provider = UserSerializer(read_only=True)
    consumer = UserSerializer(read_only=True)
    is_expired = serializers.ReadOnlyField()
    time_until_expiry = serializers.ReadOnlyField()

    class Meta:
        model = Appointment
        fields = [
            'id',
            'consumer',
            'provider',
            'service',
            'appointment_date',
            'appointment_time',
            'status',
            'notes',
            'created_at',
            'updated_at',
            'is_temporary',
            'expires_at',
            'payment_completed',
            'payment_reference',
            'is_expired',
            'time_until_expiry'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CreateAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'service',
            'appointment_date',
            'appointment_time',
            'notes'
        ]

    def validate_appointment_date(self, value):
        """Validar que la fecha no sea en el pasado"""
        if value < date.today():
            raise serializers.ValidationError("La fecha de la cita no puede ser en el pasado")
        
        # No permitir citas más de 3 meses en el futuro
        max_date = date.today() + timezone.timedelta(days=90)
        if value > max_date:
            raise serializers.ValidationError("La fecha de la cita no puede ser más de 3 meses en el futuro")
        
        return value

    def validate_appointment_time(self, value):
        """Validar que la hora esté en un rango razonable"""
        if value:
            hour = value.hour
            if hour < 6 or hour > 22:
                raise serializers.ValidationError("Las citas deben estar entre las 6:00 AM y 10:00 PM")
        return value

    def validate(self, data):
        """Validaciones adicionales"""
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        
        if not appointment_date or not appointment_time:
            raise serializers.ValidationError("Debe especificar fecha y hora")
        
        # Validar que no sea domingo (opcional)
        if appointment_date.weekday() == 6:  # 6 = domingo
            raise serializers.ValidationError("No se permiten citas los domingos")
        
        return data


class UpdateAppointmentSerializer(serializers.ModelSerializer):
    """Serializer para editar appointment completo"""
    class Meta:
        model = Appointment
        fields = [
            'appointment_date',
            'appointment_time',
            'notes'
        ]

    def validate_appointment_date(self, value):
        """Validar que la fecha no sea en el pasado"""
        if value < date.today():
            raise serializers.ValidationError("La fecha de la cita no puede ser en el pasado")
        
        # No permitir citas más de 3 meses en el futuro
        max_date = date.today() + timezone.timedelta(days=90)
        if value > max_date:
            raise serializers.ValidationError("La fecha de la cita no puede ser más de 3 meses en el futuro")
        
        return value

    def validate_appointment_time(self, value):
        """Validar que la hora esté en un rango razonable"""
        if value:
            hour = value.hour
            if hour < 6 or hour > 22:
                raise serializers.ValidationError("Las citas deben estar entre las 6:00 AM y 10:00 PM")
        return value

    def validate(self, data):
        """Validaciones adicionales"""
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        
        if appointment_date and appointment_time:
            # Validar que no sea domingo (opcional)
            if appointment_date.weekday() == 6:  # 6 = domingo
                raise serializers.ValidationError("No se permiten citas los domingos")
        
        return data


class UpdateAppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status', 'notes']

    def validate_status(self, value):
        allowed = [
            Appointment.Status.CANCELLED,
            Appointment.Status.CONFIRMED,
            Appointment.Status.COMPLETED
        ]
        if value not in allowed:
            raise serializers.ValidationError("Estado no permitido")
        return value


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalles completos del appointment"""
    service = ProviderServiceSerializer(read_only=True)
    provider = UserSerializer(read_only=True)
    consumer = UserSerializer(read_only=True)
    is_expired = serializers.ReadOnlyField()
    time_until_expiry = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'consumer',
            'provider',
            'service',
            'appointment_date',
            'appointment_time',
            'status',
            'notes',
            'created_at',
            'updated_at',
            'is_temporary',
            'expires_at',
            'payment_completed',
            'payment_reference',
            'is_expired',
            'time_until_expiry'
        ]
        read_only_fields = ['id', 'consumer', 'provider', 'service', 'created_at', 'updated_at']


class MarkAppointmentAsPaidSerializer(serializers.Serializer):
    """Serializer para marcar appointment como pagado"""
    payment_reference = serializers.CharField(max_length=100, required=False)
    
    def validate(self, data):
        appointment = self.context.get('appointment')
        if not appointment:
            raise serializers.ValidationError("Appointment no encontrado")
        
        if appointment.payment_completed:
            raise serializers.ValidationError("Este appointment ya fue marcado como pagado")
        
        if appointment.is_expired:
            raise serializers.ValidationError("Este appointment temporal ha expirado")
        
        return data
