from rest_framework import serializers
from .models import Appointment
from providers.services.serializers import ServiceSerializer
from core.serializers import UserSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    provider = UserSerializer(read_only=True)
    consumer = UserSerializer(read_only=True)

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
            'updated_at'
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

    def validate(self, data):
        # Validar disponibilidad del proveedor
        # Validar horario de servicio
        return data