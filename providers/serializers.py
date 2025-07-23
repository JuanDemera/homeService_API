from rest_framework import serializers
from core.models import User
from users.models import UserProfile
from .models import Provider

class ProviderRegisterUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    phone = serializers.CharField(max_length=15, required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)

class ProviderRegisterProfileSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=50, required=True)
    lastname = serializers.CharField(max_length=50, required=True)
    cedula = serializers.CharField(max_length=20, required=True)
    email = serializers.EmailField(required=False)
    birth_date = serializers.DateField(required=False)

class ProviderRegisterSerializer(serializers.ModelSerializer):
    user = ProviderRegisterUserSerializer(required=True)
    profile = ProviderRegisterProfileSerializer(required=True)
    documents = serializers.JSONField(required=False)

    class Meta:
        model = Provider
        fields = ['user', 'profile', 'documents', 'bio']
        extra_kwargs = {'bio': {'required': False}}

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Este teléfono ya está registrado")
        return value

    def validate_identification(self, value):
        if UserProfile.objects.filter(identification=value).exists():
            raise serializers.ValidationError("Esta cédula ya está registrada")
        return value

class ProviderVerificationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['verification_documents']
        
    def validate_verification_documents(self, value):
        if not value:
            raise serializers.ValidationError("Debe enviar al menos un documento")
        return value

class ProviderVerificationSerializer(serializers.ModelSerializer):
    action = serializers.CharField(required=True)
    reason = serializers.CharField(required=False)

    class Meta:
        model = Provider
        fields = ['action', 'reason']