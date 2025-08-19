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
    payment_method = serializers.ChoiceField(
        choices=[
            ('credit_card', 'Tarjeta de Crédito'),
            ('debit_card', 'Tarjeta de Débito'),
            ('cash', 'Efectivo'),
            ('transfer', 'Transferencia Bancaria'),
            ('paypal', 'PayPal'),
        ]
    )
    currency = serializers.ChoiceField(
        choices=[('USD', 'Dólares'), ('EUR', 'Euros')],
        default='USD'
    )
    
    # Solo referencia al appointment (opcional)
    appointment_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID del appointment si ya existe"
    )
    
    def validate_cart_id(self, value):
        from users.carts.models import Cart
        if not Cart.objects.filter(id=value).exists():
            raise serializers.ValidationError("El carrito no existe")
        return value
    
    def validate_payment_method(self, value):
        # Validaciones específicas por método de pago
        if value in ['credit_card', 'debit_card']:
            # Aquí podrías validar datos de tarjeta
            pass
        return value
    
    def validate_appointment_id(self, value):
        if value is not None:
            from users.appointments.models import Appointment
            if not Appointment.objects.filter(id=value).exists():
                raise serializers.ValidationError("El appointment especificado no existe")
        return value

class PaymentSimulationResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    transaction_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    payment_method = serializers.CharField()
    cart_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    service_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    estimated_processing_time = serializers.CharField()
    success_probability = serializers.FloatField()
    message = serializers.CharField()
    
    # Solo referencia al appointment
    appointment_id = serializers.IntegerField(allow_null=True)