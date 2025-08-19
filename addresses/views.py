from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Address
from .serializers import (
    AddressSerializer, AddressCreateSerializer, AddressUpdateSerializer,
    AddressGeolocationSerializer, AddressSuggestionSerializer
)
from .permissions import IsAddressOwner, CanManageAddresses
from core.models import User

class AddressListView(generics.ListCreateAPIView):
    """Vista para listar y crear direcciones"""
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageAddresses]
    
    def get_queryset(self):
        """Obtener direcciones del usuario actual"""
        if getattr(self, 'swagger_fake_view', False):
            return Address.objects.none()
        return Address.objects.filter(
            user=self.request.user, 
            is_active=True
        )
    
    def get_serializer_class(self):
        """Usar serializer específico para crear"""
        if self.request.method == 'POST':
            return AddressCreateSerializer
        return AddressSerializer
    
    def list(self, request, *args, **kwargs):
        """Listar direcciones con manejo de caso vacío"""
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                'message': 'No hay direcciones configuradas',
                'total_addresses': 0,
                'addresses': [],
                'has_addresses': False,
                'user_role': request.user.role,
                'max_addresses': 3 if request.user.role == 'consumer' else 1
            }, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'total_addresses': queryset.count(),
            'addresses': serializer.data,
            'has_addresses': True,
            'user_role': request.user.role,
            'max_addresses': 3 if request.user.role == 'consumer' else 1
        })

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para gestionar una dirección específica"""
    serializer_class = AddressUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAddressOwner]
    
    def get_queryset(self):
        """Obtener dirección del usuario actual"""
        if getattr(self, 'swagger_fake_view', False):
            return Address.objects.none()
        return Address.objects.filter(
            user=self.request.user, 
            is_active=True
        )
    
    def get_serializer_class(self):
        """Usar serializer específico según el método"""
        if self.request.method in ['PUT', 'PATCH']:
            return AddressUpdateSerializer
        return AddressSerializer
    
    def perform_destroy(self, instance):
        """Eliminar dirección (marcar como inactiva)"""
        instance.is_active = False
        instance.save()

class AddressGeolocationView(generics.CreateAPIView):
    """Vista para crear dirección solo con geolocalización"""
    serializer_class = AddressGeolocationSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageAddresses]
    
    def create(self, request, *args, **kwargs):
        """Crear dirección con geolocalización"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Asignar usuario
        validated_data = serializer.validated_data
        validated_data['user'] = request.user
        
        # Crear dirección
        address = Address.objects.create(**validated_data)
        
        # Serializar respuesta
        response_serializer = AddressSerializer(address, context={'request': request})
        
        return Response({
            'message': 'Dirección creada con geolocalización correctamente',
            'address': response_serializer.data
        }, status=status.HTTP_201_CREATED)

class AddressDefaultView(generics.RetrieveAPIView):
    """Vista para obtener la dirección por defecto"""
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageAddresses]
    
    def get_object(self):
        """Obtener dirección por defecto del usuario"""
        return get_object_or_404(
            Address, 
            user=self.request.user, 
            is_default=True, 
            is_active=True
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageAddresses])
def set_default_address(request, address_id):
    """Establecer una dirección como predeterminada"""
    try:
        address = get_object_or_404(
            Address, 
            id=address_id, 
            user=request.user, 
            is_active=True
        )
        
        # Desmarcar otras direcciones como default
        Address.objects.filter(
            user=request.user, 
            is_default=True
        ).update(is_default=False)
        
        # Marcar esta como default
        address.is_default = True
        address.save()
        
        return Response({
            'message': 'Dirección establecida como predeterminada correctamente',
            'address_id': address.id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanManageAddresses])
def address_suggestions(request):
    """Obtener sugerencias de direcciones (simulado)"""
    query = request.GET.get('query', '')
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    
    if not query:
        return Response({
            'error': 'El parámetro "query" es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Simular sugerencias de Ecuador (en producción usarías Google Places API)
    suggestions = [
        {
            'id': 1,
            'description': f'{query}, Guayaquil, Ecuador',
            'place_id': 'place_1',
            'structured_formatting': {
                'main_text': query,
                'secondary_text': 'Guayaquil, Ecuador'
            },
            'geometry': {
                'location': {
                    'lat': -2.1894,
                    'lng': -79.8891
                }
            }
        },
        {
            'id': 2,
            'description': f'{query}, Quito, Ecuador',
            'place_id': 'place_2',
            'structured_formatting': {
                'main_text': query,
                'secondary_text': 'Quito, Ecuador'
            },
            'geometry': {
                'location': {
                    'lat': -0.2299,
                    'lng': -78.5249
                }
            }
        },
        {
            'id': 3,
            'description': f'{query}, Cuenca, Ecuador',
            'place_id': 'place_3',
            'structured_formatting': {
                'main_text': query,
                'secondary_text': 'Cuenca, Ecuador'
            },
            'geometry': {
                'location': {
                    'lat': -2.9006,
                    'lng': -79.0045
                }
            }
        },
        {
            'id': 4,
            'description': f'{query}, Manta, Ecuador',
            'place_id': 'place_4',
            'structured_formatting': {
                'main_text': query,
                'secondary_text': 'Manta, Ecuador'
            },
            'geometry': {
                'location': {
                    'lat': -0.9677,
                    'lng': -80.7089
                }
            }
        }
    ]
    
    return Response({
        'predictions': suggestions,
        'status': 'OK'
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanManageAddresses])
def address_summary(request):
    """Obtener resumen de direcciones del usuario"""
    addresses = Address.objects.filter(
        user=request.user, 
        is_active=True
    )
    
    default_address = addresses.filter(is_default=True).first()
    
    return Response({
        'user_role': request.user.role,
        'max_addresses': 3 if request.user.role == 'consumer' else 1,
        'total_addresses': addresses.count(),
        'has_default': default_address is not None,
        'default_address': AddressSerializer(default_address, context={'request': request}).data if default_address else None,
        'all_addresses': AddressSerializer(addresses, context={'request': request}, many=True).data
    })
