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
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = str(user.id)
        token['role'] = user.role
        token['is_verified'] = user.is_verified
        token['username'] = user.username
        token['phone'] = user.phone
        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except Exception:
            raise serializers.ValidationError(
                _('No tiene cuenta registrada'),
                code='no_account'
            )
        if not self.user.is_active:
            raise serializers.ValidationError(
                _('Usuario inactivo, comuníquese con Home Service'),
                code='account_disabled'
            )
        if self.user.disabled:
            raise serializers.ValidationError(
                _('Account suspended: ') + (self.user.disabled_reason or _('No reason provided')),
                code='account_suspended'
            )
        self.user.save()
        return data