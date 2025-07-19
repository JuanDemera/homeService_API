from rest_framework import serializers
from .models import FeePolicy , Category
from providers.services.serializers import CategorySerializer

class FeePolicySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    created_by = serializers.StringRelatedField(read_only=True)
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = FeePolicy
        fields = [
            'id',
            'category',
            'category_id',
            'fee_percentage',
            'valid_from',
            'valid_to',
            'is_active',
            'created_by',
            'created_at',
            'is_current'
        ]
        read_only_fields = ['created_by', 'created_at']

    def get_is_current(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        return (obj.valid_from <= today and 
                (obj.valid_to is None or obj.valid_to >= today) and
                obj.is_active)

    def validate(self, data):
        if data.get('valid_to') and data['valid_to'] < data['valid_from']:
            raise serializers.ValidationError(
                {"valid_to": "La fecha de fin debe ser posterior a la fecha de inicio"}
            )
        return data