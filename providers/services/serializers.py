from rest_framework import serializers
from decimal import Decimal
from .models import Category, Service
from providers.models import Provider

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon_url', 'is_active']
        read_only_fields = fields
        ref_name = 'ServiceCategory'


class ProviderServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    provider_name = serializers.SerializerMethodField()
    photo = serializers.URLField(required=False, allow_null=True)

    class Meta:
        model = Service
        fields = [
            'id', 'title', 'description', 'category', 'price',
            'duration_minutes', 'is_active', 'provider_name', 'photo',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'provider_name']
        ref_name = 'ProviderService'

    def get_provider_name(self, obj):
        return obj.provider.user.username


class ServiceCreateSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    photo = serializers.URLField(required=False, allow_null=True)

    class Meta:
        model = Service
        fields = [
            'id', 'title', 'description', 'category', 'price',
            'duration_minutes', 'is_active', 'photo'
        ]
        read_only_fields = ['id']
        ref_name = 'ServiceCreate'


class ServiceUpdateSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    photo = serializers.URLField(required=False, allow_null=True)

    class Meta:
        model = Service
        fields = [
            'title', 'description', 'category', 'price',
            'duration_minutes', 'is_active', 'photo'
        ]
        ref_name = 'ServiceUpdate'


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon_url', 'is_active']
        read_only_fields = ['id']
