from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from decimal import Decimal
from .models import Category, Service

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon_url', 'is_active']
        read_only_fields = fields  

class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source='category',
        write_only=True
    )
    provider_name = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'title', 'description', 'category', 'category_id',
            'price', 'duration_minutes', 'is_active', 'provider_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'provider_name']

    @extend_schema_field(str)
    def get_provider_name(self, obj) -> str:
        return obj.provider.user.username

class ServiceCreateSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )

    class Meta:
        model = Service
        fields = [
            'title', 'description', 'category', 'price',
            'duration_minutes', 'is_active'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def create(self, validated_data):
        provider = self.context['request'].user.provider
        return Service.objects.create(provider=provider, **validated_data)