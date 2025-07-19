from rest_framework import serializers
from decimal import Decimal
from .models import ProviderPayment

class ProviderPaymentSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )

    class Meta:
        model = ProviderPayment
        fields = [
            'id', 'amount', 'transaction_type', 'description',
            'is_completed', 'created_at', 'completed_at'
        ]
        read_only_fields = ['is_completed', 'created_at', 'completed_at']

class PaymentSimulationSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField(min_value=1)
    payment_method = serializers.CharField(max_length=50)

    
    def validate_cart_id(self, value):
        from carts.models import Cart
        if not Cart.objects.filter(id=value).exists():
            raise serializers.ValidationError("Cart does not exist")
        return value