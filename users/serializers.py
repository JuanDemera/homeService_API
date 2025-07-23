from rest_framework import serializers
from core.models import User
from users.models import UserProfile
import phonenumbers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['firstname', 'lastname', 'email', 'cedula', 'birth_date', 'edad']
        read_only_fields = ['edad']

class GuestProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['firstname', 'lastname', 'email']
        read_only_fields = ['email']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'role']

class GuestSerializer(serializers.ModelSerializer):
    profile = GuestProfileSerializer()  
    
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'role', 'profile']
        read_only_fields = fields
        extra_kwargs = {
            'username': {'required': False},
            'role': {'read_only': True}
        }

class OTPSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)

    def validate_phone(self, value):
        print("Número recibido:", value)  # Para debug
        try:
            phone = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone):
                raise serializers.ValidationError("Número de teléfono inválido")
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            print("Error phonenumbers:", e)  # Para debug
            raise serializers.ValidationError("Número de teléfono inválido")

class VerifyOTPSerializer(OTPSerializer):  
    otp = serializers.CharField(required=True, min_length=4, max_length=6)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("El código OTP debe contener solo números")
        return value

class RegisterConsumerSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(max_length=100, write_only=True)
    lastname = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(write_only=True)
    cedula = serializers.CharField(max_length=20, write_only=True)
    birth_date = serializers.DateField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'phone', 'password', 'firstname', 'lastname', 'email', 'cedula', 'birth_date']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_phone(self, value):
        print("Número recibido:", value)  # Para debug
        try:
            phone = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone):
                raise serializers.ValidationError("Número de teléfono inválido")
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            print("Error phonenumbers:", e)  # Para debug
            raise serializers.ValidationError("Número de teléfono inválido")

    def validate_email(self, value):
        try:
            validate_email(value)
            if UserProfile.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError("Este email ya está registrado")
            return value.lower()
        except ValidationError:
            raise serializers.ValidationError("Email inválido")

    def validate_cedula(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("La cédula debe contener solo números")
        if UserProfile.objects.filter(cedula=value).exists():
            raise serializers.ValidationError("Esta cédula ya está registrada")
        return value

    def create(self, validated_data):
        profile_data = {
            'firstname': validated_data.pop('firstname'),
            'lastname': validated_data.pop('lastname'),
            'email': validated_data.pop('email'),
            'cedula': validated_data.pop('cedula'),
            'birth_date': validated_data.pop('birth_date'),
        }
        
        user = User.objects.create_user(
            username=validated_data['username'],
            phone=validated_data['phone'],
            password=validated_data['password'],
            role=User.Role.CONSUMER,
            is_verified=True
        )
        
        UserProfile.objects.create(user=user, **profile_data)
        return user