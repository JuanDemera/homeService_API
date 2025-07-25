from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from core.models import User
from users.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['firstname', 'lastname', 'email', 'cedula', 'birth_date', 'edad']
        read_only_fields = ['edad']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone', 'role', 'is_verified',
            'is_active', 'created_at', 'profile'
        ]
        read_only_fields = ['id', 'created_at']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        phone = attrs.get('phone')
        user = None

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
        elif phone:
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError(
                {'detail': _('No tiene cuenta registrada')},
                code='no_account'
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {'detail': _('Usuario inactivo, comuníquese con Home Service')},
                code='account_disabled'
            )

        return super().validate(attrs)