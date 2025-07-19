from rest_framework import serializers
from decimal import Decimal
from .models import Category, Service

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon_url', 'is_active']
        read_only_fields = fields
        ref_name = 'ServiceCategory' 

class ProviderServiceSerializer(serializers.ModelSerializer): 
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
        ref_name = 'ProviderService'  
    
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
        ref_name = 'ServiceCreate'  