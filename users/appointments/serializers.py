from rest_framework import serializers
from .models import Appointment
from providers.services.serializers import ProviderServiceSerializer
from core.serializers import UserSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    service = ProviderServiceSerializer(read_only=True)
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
        if data['appointment_date'] is None or data['appointment_time'] is None:
            raise serializers.ValidationError("Debe especificar fecha y hora")
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
