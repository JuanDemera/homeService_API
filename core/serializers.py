from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
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
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError(
                {'detail': _('No tiene cuenta registrada')},
                code='no_account'
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {'detail': _('Usuario inactivo, comuníquese con Home Service')},
                code='account_disabled'
            )
        refresh = self.get_token(user)
        access = refresh.access_token
        return {
            'refresh': str(refresh),
            'access': str(access)
        }