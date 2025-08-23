from rest_framework import serializers
from .models import Address
from core.models import User

# Constantes para mensajes de validación
ECUADOR_ONLY_MESSAGE = "Solo se permiten direcciones de Ecuador."

class AddressSerializer(serializers.ModelSerializer):
    """Serializer para direcciones"""
    coordinates = serializers.SerializerMethodField()
    has_coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = Address
        fields = [
            'id', 'title', 'street', 'city', 'state', 'postal_code', 
            'country', 'latitude', 'longitude', 'formatted_address',
            'is_default', 'is_active', 'created_at', 'updated_at',
            'coordinates', 'has_coordinates'
        ]
        read_only_fields = ['id', 'formatted_address', 'created_at', 'updated_at']
    
    def get_coordinates(self, obj):
        """Obtener coordenadas como tupla"""
        return obj.coordinates
    
    def get_has_coordinates(self, obj):
        """Verificar si tiene coordenadas"""
        return obj.has_coordinates
    
    def validate(self, data):
        """Validar límites de direcciones por tipo de usuario y país"""
        # Validar que sea Ecuador
        country = data.get('country', 'Ecuador')
        if country and country.lower() not in ['ecuador', 'ec']:
            raise serializers.ValidationError(ECUADOR_ONLY_MESSAGE)
        
        user = self.context['request'].user
        
        # Contar direcciones existentes (excluyendo la actual si es update)
        existing_count = Address.objects.filter(
            user=user, 
            is_active=True
        ).count()
        
        # Si es una nueva dirección, verificar límites
        if self.instance is None:
            if user.role == User.Role.CONSUMER and existing_count >= 3:
                raise serializers.ValidationError(
                    "Los usuarios consumer pueden tener máximo 3 direcciones."
                )
            elif user.role == User.Role.PROVIDER and existing_count >= 1:
                raise serializers.ValidationError(
                    "Los providers pueden tener máximo 1 dirección."
                )
        
        return data
    
    def create(self, validated_data):
        """Crear dirección asignando el usuario actual"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AddressCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear direcciones con geolocalización"""
    
    class Meta:
        model = Address
        fields = [
            'title', 'street', 'city', 'state', 'postal_code', 
            'country', 'latitude', 'longitude', 'is_default'
        ]
    
    def validate(self, data):
        """Validar que al menos tenga coordenadas o dirección manual y sea Ecuador"""
        # Validar que sea Ecuador
        country = data.get('country', 'Ecuador')
        if country and country.lower() not in ['ecuador', 'ec']:
            raise serializers.ValidationError(ECUADOR_ONLY_MESSAGE)
        
        has_coordinates = data.get('latitude') and data.get('longitude')
        has_manual_address = data.get('street') or data.get('city')
        
        if not has_coordinates and not has_manual_address:
            raise serializers.ValidationError(
                "Debe proporcionar coordenadas geográficas o dirección manual."
            )
        
        return data
    
    def create(self, validated_data):
        """Crear dirección asignando el usuario actual"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AddressUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar direcciones"""
    
    class Meta:
        model = Address
        fields = [
            'title', 'street', 'city', 'state', 'postal_code', 
            'country', 'latitude', 'longitude', 'is_default'
        ]
    
    def validate(self, data):
        """Validar que al menos tenga coordenadas o dirección manual y sea Ecuador"""
        # Validar que sea Ecuador
        country = data.get('country', 'Ecuador')
        if country and country.lower() not in ['ecuador', 'ec']:
            raise serializers.ValidationError(ECUADOR_ONLY_MESSAGE)
        
        # Obtener datos actuales
        instance = self.instance
        current_lat = instance.latitude if instance else None
        current_lng = instance.longitude if instance else None
        current_street = instance.street if instance else None
        current_city = instance.city if instance else None
        
        # Datos nuevos
        new_lat = data.get('latitude', current_lat)
        new_lng = data.get('longitude', current_lng)
        new_street = data.get('street', current_street)
        new_city = data.get('city', current_city)
        
        has_coordinates = new_lat and new_lng
        has_manual_address = new_street or new_city
        
        if not has_coordinates and not has_manual_address:
            raise serializers.ValidationError(
                "Debe proporcionar coordenadas geográficas o dirección manual."
            )
        
        return data

class AddressGeolocationSerializer(serializers.ModelSerializer):
    """Serializer para crear direcciones solo con geolocalización"""
    
    class Meta:
        model = Address
        fields = ['title', 'latitude', 'longitude', 'is_default']
    
    def validate_latitude(self, value):
        """Validar latitud de Ecuador"""
        if value and (value < -5.0 or value > 1.5):
            raise serializers.ValidationError(
                "La latitud debe estar dentro del rango de Ecuador (-5.0 a 1.5 grados)."
            )
        return value
    
    def validate_longitude(self, value):
        """Validar longitud de Ecuador"""
        if value and (value < -81.5 or value > -75.0):
            raise serializers.ValidationError(
                "La longitud debe estar dentro del rango de Ecuador (-81.5 a -75.0 grados)."
            )
        return value
    
    def validate(self, data):
        """Validar que tenga ambas coordenadas"""
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            raise serializers.ValidationError(
                "Debe proporcionar tanto latitud como longitud."
            )
        
        return data
    
    def create(self, validated_data):
        """Crear dirección con geolocalización"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AddressSuggestionSerializer(serializers.Serializer):
    """Serializer para sugerencias de direcciones"""
    query = serializers.CharField(
        max_length=200,
        help_text="Texto para buscar sugerencias de direcciones"
    )
    latitude = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False,
        help_text="Latitud para búsqueda localizada"
    )
    longitude = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False,
        help_text="Longitud para búsqueda localizada"
    ) 