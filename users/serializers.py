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

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']

class RegisterConsumerSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(max_length=100)
    lastname = serializers.CharField(max_length=100)
    email = serializers.CharField()
    cedula = serializers.CharField(max_length=20)
    birth_date = serializers.DateField()

    class Meta:
        model = User
        fields = ['username', 'phone', 'password', 'firstname', 'lastname', 'email', 'cedula', 'birth_date']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_phone(self, value):
        try:
            phone = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone):
                raise serializers.ValidationError("Número de teléfono inválido")
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except:
            raise serializers.ValidationError("Número de teléfono inválido")

    def validate_email(self, value):
        try:
            validate_email(value)
            return value.lower()
        except ValidationError:
            raise serializers.ValidationError("Email inválido")

    def validate_cedula(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("La cédula debe contener solo números")
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