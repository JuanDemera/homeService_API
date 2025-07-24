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
    photo = serializers.URLField(required=False, allow_null=True)

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

class RegisterProviderSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(max_length=100, write_only=True)
    lastname = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(write_only=True)
    cedula = serializers.CharField(max_length=20, write_only=True)
    birth_date = serializers.DateField(write_only=True)
    photo = serializers.URLField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'username', 'phone', 'password', 'firstname', 'lastname',
            'email', 'cedula', 'birth_date', 'photo'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        profile_data = {
            'firstname': validated_data.pop('firstname'),
            'lastname': validated_data.pop('lastname'),
            'email': validated_data.pop('email'),
            'cedula': validated_data.pop('cedula'),
            'birth_date': validated_data.pop('birth_date'),
            'photo': validated_data.pop('photo', None),
        }
        user = User.objects.create_user(
            username=validated_data['username'],
            phone=validated_data['phone'],
            password=validated_data['password'],
            role=User.Role.PROVIDER,
            is_verified=True
        )
        UserProfile.objects.create(user=user, **profile_data)
        return user