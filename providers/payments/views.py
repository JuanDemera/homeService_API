from rest_framework import generics, permissions, status
from rest_framework.response import Response
from decimal import Decimal
import uuid
import random
from django.db import transaction
from django.utils import timezone
from .models import ProviderPayment
from .serializers import (
    ProviderPaymentSerializer, 
    PaymentSimulationSerializer,
    PaymentSimulationResponseSerializer
)

class ProviderPaymentListView(generics.ListAPIView):
    serializer_class = ProviderPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ProviderPayment.objects.none()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProviderPayment.objects.none()
        return ProviderPayment.objects.filter(
            provider__user=self.request.user
        ).order_by('-created_at')

class PaymentSimulationView(generics.GenericAPIView):
    serializer_class = PaymentSimulationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart_id = serializer.validated_data['cart_id']
        payment_method = serializer.validated_data['payment_method']
        currency = serializer.validated_data.get('currency', 'USD')
        appointment_id = serializer.validated_data.get('appointment_id')
        
        try:
            with transaction.atomic():
                # Obtener información del carrito
                from users.carts.models import Cart
                cart = Cart.objects.get(id=cart_id)
                
                # Verificar que el carrito pertenece al usuario
                if cart.user != request.user:
                    return Response({
                        'error': 'No tienes permisos para acceder a este carrito'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Obtener el primer item del carrito (asumiendo un servicio por carrito)
                cart_item = cart.items.first()
                if not cart_item:
                    return Response({
                        'error': 'El carrito está vacío'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                service = cart_item.service
                provider = service.provider
                
                # Si se proporciona appointment_id, verificar que existe y pertenece al usuario
                appointment = None
                if appointment_id:
                    from users.appointments.models import Appointment
                    try:
                        appointment = Appointment.objects.get(id=appointment_id)
                        if appointment.consumer != request.user:
                            return Response({
                                'error': 'No tienes permisos para acceder a este appointment'
                            }, status=status.HTTP_403_FORBIDDEN)
                        
                        # Verificar que el appointment sea temporal y no expirado
                        if not appointment.is_temporary:
                            return Response({
                                'error': 'El appointment ya no es temporal'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        
                        if appointment.is_expired:
                            return Response({
                                'error': 'El appointment temporal ha expirado'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        
                        if appointment.payment_completed:
                            return Response({
                                'error': 'El appointment ya fue marcado como pagado'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        
                    except Appointment.DoesNotExist:
                        return Response({
                            'error': 'El appointment especificado no existe'
                        }, status=status.HTTP_404_NOT_FOUND)
                
                # Calcular montos
                cart_total = self._calculate_cart_total(cart)
                service_fee = self._calculate_service_fee(cart_total, payment_method)
                total_amount = cart_total + service_fee
                
                # Generar simulación realista
                simulation_data = self._generate_simulation(
                    cart_total=cart_total,
                    service_fee=service_fee,
                    total_amount=total_amount,
                    payment_method=payment_method,
                    currency=currency
                )
                
                # Marcar appointment como pagado si existe
                if appointment:
                    payment_reference = simulation_data['transaction_id']
                    appointment.mark_as_paid(payment_reference)
                
                # Agregar información del appointment a la respuesta
                simulation_data.update({
                    'appointment_id': appointment_id,
                })
                
                # Limpiar el carrito después del pago exitoso
                cart.items.all().delete()
                
                # Serializar respuesta
                response_serializer = PaymentSimulationResponseSerializer(simulation_data)
                
                return Response(response_serializer.data, status=status.HTTP_200_OK)
                
        except Cart.DoesNotExist:
            return Response({
                'error': 'El carrito especificado no existe'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error en la simulación: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_cart_total(self, cart):
        """Calcular el total del carrito"""
        try:
            # Aquí deberías implementar la lógica real de cálculo
            # Por ahora simulamos un total
            return Decimal('150.00')
        except Exception:
            return Decimal('0.00')
    
    def _calculate_service_fee(self, cart_total, payment_method):
        """Calcular comisión de servicio según método de pago"""
        fee_percentages = {
            'credit_card': Decimal('0.035'),  # 3.5%
            'debit_card': Decimal('0.025'),   # 2.5%
            'cash': Decimal('0.020'),         # 2.0%
            'transfer': Decimal('0.015'),     # 1.5%
            'paypal': Decimal('0.029'),       # 2.9%
        }
        
        percentage = fee_percentages.get(payment_method, Decimal('0.030'))
        return cart_total * percentage
    
    def _generate_simulation(self, cart_total, service_fee, total_amount, payment_method, currency):
        """Generar datos de simulación realistas"""
        
        # Probabilidades de éxito por método de pago
        success_rates = {
            'credit_card': 0.95,
            'debit_card': 0.98,
            'cash': 1.0,
            'transfer': 0.92,
            'paypal': 0.97,
        }
        
        # Tiempos de procesamiento estimados
        processing_times = {
            'credit_card': '2-3 segundos',
            'debit_card': '1-2 segundos',
            'cash': 'Inmediato',
            'transfer': '1-3 días hábiles',
            'paypal': '30-60 segundos',
        }
        
        # Generar ID de transacción único
        transaction_id = f"sim_{uuid.uuid4().hex[:8]}_{int(timezone.now().timestamp())}"
        
        # Calcular probabilidad de éxito
        base_success_rate = success_rates.get(payment_method, 0.90)
        # Añadir variabilidad basada en el monto
        if total_amount > Decimal('500.00'):
            base_success_rate *= 0.95  # Menor probabilidad para montos altos
        
        success_probability = min(base_success_rate, 1.0)
        
        # Mensajes personalizados
        messages = {
            'credit_card': 'Transacción simulada exitosamente. Verifique los datos de su tarjeta.',
            'debit_card': 'Pago con débito procesado. Fondos disponibles verificados.',
            'cash': 'Pago en efectivo confirmado. Coordine la entrega con el proveedor.',
            'transfer': 'Transferencia bancaria iniciada. Confirme el pago con su banco.',
            'paypal': 'Pago PayPal procesado. Verifique su cuenta de PayPal.',
        }
        
        return {
            'status': 'simulation_success',
            'transaction_id': transaction_id,
            'amount': str(total_amount),
            'currency': currency,
            'payment_method': payment_method,
            'cart_total': str(cart_total),
            'service_fee': str(service_fee),
            'total_amount': str(total_amount),
            'estimated_processing_time': processing_times.get(payment_method, 'Variable'),
            'success_probability': round(success_probability, 3),
            'message': messages.get(payment_method, 'Simulación completada exitosamente.'),
        }

class PaymentHistoryView(generics.ListAPIView):
    """Vista mejorada para historial de pagos"""
    serializer_class = ProviderPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProviderPayment.objects.none()
        return ProviderPayment.objects.filter(
            provider__user=self.request.user
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Calcular estadísticas
        total_payments = queryset.count()
        completed_payments = queryset.filter(is_completed=True).count()
        total_amount = sum(payment.amount for payment in queryset if payment.is_completed)
        
        return Response({
            'payments': serializer.data,
            'statistics': {
                'total_payments': total_payments,
                'completed_payments': completed_payments,
                'pending_payments': total_payments - completed_payments,
                'total_amount': str(total_amount),
                'success_rate': round(completed_payments / total_payments * 100, 2) if total_payments > 0 else 0
            }
        })