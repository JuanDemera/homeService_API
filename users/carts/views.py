from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from providers.services.models import Service

class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 2))  # Cache por 2 minutos
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        cart = Cart.objects.filter(user=self.request.user).first()
        if not cart:
            raise NotFound({'error': 'Carrito no encontrado'})
        return cart

class AddToCartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service_id = serializer.validated_data['service'].id
        quantity = serializer.validated_data.get('quantity', 1)
        
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            raise NotFound({'error': 'Carrito no encontrado'})
        
        try:
            service = Service.objects.select_for_update().get(id=service_id)
        except Service.DoesNotExist:
            raise NotFound({'error': 'Servicio no encontrado'})
        
        if not service.is_available:
            return Response(
                {'error': 'Este servicio no está disponible actualmente'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                service=service,
                defaults={'quantity': quantity}
            )
            
            if not created:
                item.quantity += quantity
                item.save()
        
        return Response(
            {'message': 'Servicio agregado al carrito'},
            status=status.HTTP_200_OK
        )

class RemoveFromCartView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        service_id = request.data.get('service_id')
        if not service_id:
            return Response(
                {'error': 'service_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            raise NotFound({'error': 'Carrito no encontrado'})
        
        try:
            item = CartItem.objects.get(cart=cart, service_id=service_id)
            item.delete()
            return Response(
                {'message': 'Servicio eliminado del carrito'},
                status=status.HTTP_200_OK
            )
        except CartItem.DoesNotExist:
            raise NotFound({'error': 'Servicio no encontrado en el carrito'})