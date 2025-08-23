from rest_framework import serializers
from core.models import User
from users.models import UserProfile
import phonenumbers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# Constantes de error reutilizables para eliminar duplicity
INVALID_PHONE_ERROR = "Número de teléfono inválido"
INVALID_OTP_ERROR = "El código OTP debe contener solo números"
INVALID_EMAIL_ERROR = "Email inválido"
DUPLICATE_EMAIL_ERROR = "Este email ya está registrado"
DUPLICATE_CEDULA_ERROR = "Esta cédula ya está registrada"
INVALID_CEDULA_ERROR = "La cédula debe contener solo números"

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

# Serializer para obtener el perfil completo del usuario consumer
class ConsumerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'username', 'phone', 'role', 'firstname', 'lastname', 
            'email', 'cedula', 'birth_date', 'edad', 'photo'
        ]
        read_only_fields = ['edad']

# Serializer para actualizar el perfil del usuario consumer
class UpdateConsumerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    phone = serializers.CharField(source='user.phone')
    
    class Meta:
        model = UserProfile
        fields = [
            'username', 'phone', 'firstname', 'lastname', 
            'email', 'cedula', 'birth_date'
        ]

    def validate_phone(self, value):
        try:
            phone = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone):
                raise serializers.ValidationError(INVALID_PHONE_ERROR)
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            raise serializers.ValidationError(INVALID_PHONE_ERROR)

    def validate_email(self, value):
        try:
            validate_email(value)
            # Verificar que el email no esté en uso por otro usuario
            if UserProfile.objects.filter(email__iexact=value).exclude(user=self.instance.user).exists():
                raise serializers.ValidationError(DUPLICATE_EMAIL_ERROR)
            return value.lower()
        except ValidationError:
            raise serializers.ValidationError(INVALID_EMAIL_ERROR)

    def validate_cedula(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(INVALID_CEDULA_ERROR)
        # Verificar que la cédula no esté en uso por otro usuario
        if UserProfile.objects.filter(cedula=value).exclude(user=self.instance.user).exists():
            raise serializers.ValidationError(DUPLICATE_CEDULA_ERROR)
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Actualizar datos del usuario
        if user_data:
            user = instance.user
            if 'username' in user_data:
                user.username = user_data['username']
            if 'phone' in user_data:
                user.phone = user_data['phone']
            user.save()
        
        # Actualizar datos del perfil
        return super().update(instance, validated_data)

# Serializer para cambiar contraseña
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta")
        return value

    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("La nueva contraseña debe tener al menos 6 caracteres")
        return value
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden'
            })
        return data

class OTPSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)

    def validate_phone(self, value):
        print("Número recibido:", value)  # Para debug
        try:
            phone = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone):
                raise serializers.ValidationError(INVALID_PHONE_ERROR)
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            print("Error phonenumbers:", e)  # Para debug
            raise serializers.ValidationError(INVALID_PHONE_ERROR)

class VerifyOTPSerializer(OTPSerializer):  
    otp = serializers.CharField(required=True, min_length=4, max_length=6)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(INVALID_OTP_ERROR)
        return value

class RegisterConsumerSerializer(serializers.ModelSerializer):
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

    def validate_phone(self, value):
        try:
            phone = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone):
                raise serializers.ValidationError(INVALID_PHONE_ERROR)
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            raise serializers.ValidationError(INVALID_PHONE_ERROR)

    def validate_email(self, value):
        try:
            validate_email(value)
            if UserProfile.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError(DUPLICATE_EMAIL_ERROR)
            return value.lower()
        except ValidationError:
            raise serializers.ValidationError(INVALID_EMAIL_ERROR)

    def validate_cedula(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(INVALID_CEDULA_ERROR)
        if UserProfile.objects.filter(cedula=value).exists():
            raise serializers.ValidationError(DUPLICATE_CEDULA_ERROR)
        return value

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
            role=User.Role.CONSUMER,
            is_verified=True
        )
        
        UserProfile.objects.create(user=user, **profile_data)
        return user 