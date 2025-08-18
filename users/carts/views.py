from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from providers.services.models import Service


class CartDetailView(generics.RetrieveAPIView):
    """
    Obtener el carrito del usuario autenticado
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartView(generics.GenericAPIView):
    """
    Agregar un servicio al carrito o actualizar su cantidad
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['service_id'],
            properties={
                'service_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del servicio"),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Cantidad (default=1)")
            },
        ),
        responses={200: CartItemSerializer}
    )
    def post(self, request, *args, **kwargs):
        service_id = request.data.get("service_id")
        quantity = int(request.data.get("quantity", 1))

        if not service_id:
            return Response({"error": "service_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            raise NotFound("El servicio no existe")

        if not service.is_active:  
            raise PermissionDenied("Este servicio no está disponible actualmente")

        cart, _ = Cart.objects.get_or_create(user=request.user)

        with transaction.atomic():
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                service=service,
                defaults={"quantity": quantity}
            )
            if not created:
                item.quantity += quantity
                item.save()

        return Response(
            {
                "message": "Servicio agregado al carrito" if created else "Cantidad actualizada",
                "item": CartItemSerializer(item).data,
                "cart": CartSerializer(cart).data
            },
            status=status.HTTP_200_OK
        )


class RemoveFromCartView(generics.GenericAPIView):
    """
    Eliminar un servicio del carrito
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['service_id'],
            properties={
                'service_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del servicio"),
            },
        ),
        responses={200: CartSerializer}
    )
    def delete(self, request, *args, **kwargs):
        service_id = request.data.get("service_id")
        if not service_id:
            return Response({"error": "service_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.get(user=request.user)

        try:
            item = CartItem.objects.get(cart=cart, service_id=service_id)
        except CartItem.DoesNotExist:
            raise NotFound("Servicio no encontrado en el carrito")

        item.delete()

        return Response(
            {"message": "Servicio eliminado del carrito", "cart": CartSerializer(cart).data},
            status=status.HTTP_200_OK
        )
