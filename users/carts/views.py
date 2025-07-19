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
    
    @method_decorator(cache_page(60 * 2))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

class AddToCartView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    
    def perform_create(self, serializer):
        cart = Cart.objects.get_or_create(user=self.request.user)[0]
        service = serializer.validated_data['service']
        quantity = serializer.validated_data.get('quantity', 1)
        
        if not service.is_available:
            raise PermissionDenied('Este servicio no está disponible actualmente')
        
        with transaction.atomic():
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                service=service,
                defaults={'quantity': quantity}
            )
            
            if not created:
                item.quantity += quantity
                item.save()

class RemoveFromCartView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    
    def get_object(self):
        cart = Cart.objects.get(user=self.request.user)
        service_id = self.request.data.get('service_id')
        
        if not service_id:
            raise serializers.ValidationError({'service_id': 'Este campo es requerido'})
        
        try:
            return CartItem.objects.get(cart=cart, service_id=service_id)
        except CartItem.DoesNotExist:
            raise NotFound('Servicio no encontrado en el carrito')
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Servicio eliminado del carrito'},
            status=status.HTTP_200_OK
        )