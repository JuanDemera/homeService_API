from rest_framework import serializers
from .models import Category, Service

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon_url', 'is_active']

class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source='category',
        write_only=True
    )
    provider_name = serializers.CharField(source='provider.user.username', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'title', 'description', 'category', 'category_id',
            'price', 'duration_minutes', 'is_active', 'provider_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['provider_name', 'created_at', 'updated_at']

class ServiceCreateSerializer(serializers.ModelSerializer):
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