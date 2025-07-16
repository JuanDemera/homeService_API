from rest_framework import serializers
from core.serializers import UserSerializer, UserProfileSerializer
from .models import Provider

class ProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile = UserProfileSerializer(source='user.profile', read_only=True)
    full_name = serializers.SerializerMethodField()
    verification_status = serializers.CharField(read_only=True)

    class Meta:
        model = Provider
        fields = [
            'id', 'user', 'profile', 'full_name', 'bio', 'rating',
            'total_completed_services', 'is_active', 'verification_status',
            'verified_at', 'created_at'
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        if hasattr(obj.user, 'profile'):
            return f"{obj.user.profile.firstname} {obj.user.profile.lastname}"
        return ""

class ProviderRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['bio']
        extra_kwargs = {'bio': {'required': False}}

    def create(self, validated_data):
        user = self.context['request'].user
        if hasattr(user, 'provider'):
            raise serializers.ValidationError("User is already a provider")
        
        provider = Provider.objects.create(
            user=user,
            **validated_data
        )
        # El usuario sigue siendo 'guest' hasta ser aprobado
        return provider

class ProviderVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['verification_status', 'rejection_reason']
        extra_kwargs = {
            'rejection_reason': {'required': False}
        }

    def validate(self, data):
        if data.get('verification_status') == 'rejected' and not data.get('rejection_reason'):
            raise serializers.ValidationError("Debe proporcionar una razón para el rechazo")
        return data