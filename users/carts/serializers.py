from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from decimal import Decimal
from .models import Cart, CartItem
from providers.services.models import Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'price', 'duration_minutes']

class CartItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source='service',
        write_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'service', 'service_id', 'quantity', 'added_at', 'total_price']
        read_only_fields = ['added_at']

    @extend_schema_field(Decimal)
    def get_total_price(self, obj) -> Decimal:
        return obj.total_price

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'updated_at', 'items', 'total_items', 'subtotal']
        read_only_fields = fields

    @extend_schema_field(int)
    def get_total_items(self, obj) -> int:
        return obj.total_items

    @extend_schema_field(Decimal)
    def get_subtotal(self, obj) -> Decimal:
        return obj.subtotal