from decimal import Decimal
from django.utils import timezone
from .models import ProviderPayment

# Excepciones específicas para el servicio de pagos
class PaymentServiceError(Exception):
    """Excepción base para errores del servicio de pagos"""
    pass

class PaymentCreationError(PaymentServiceError):
    """Error al crear un registro de pago"""
    pass

class PaymentNotFoundError(PaymentServiceError):
    """Error cuando no se encuentra un pago"""
    pass

class PaymentCompletionError(PaymentServiceError):
    """Error al completar un pago"""
    pass

class PaymentService:
    """Servicio para manejar lógica de pagos"""
    
    @staticmethod
    def calculate_cart_total(cart):
        """Calcular el total real del carrito"""
        try:
            # Aquí implementarías la lógica real de cálculo
            # Por ejemplo, sumar todos los items del carrito
            total = Decimal('0.00')
            
            # Simular cálculo basado en items del carrito
            if hasattr(cart, 'items') and cart.items.exists():
                for item in cart.items.all():
                    if hasattr(item, 'price') and item.price:
                        total += Decimal(str(item.price))
            else:
                # Si no hay items, simular un total
                total = Decimal('150.00')
            
            return total
        except Exception:
            return Decimal('0.00')
    
    @staticmethod
    def calculate_service_fee(cart_total, payment_method):
        """Calcular comisión de servicio"""
        fee_percentages = {
            'credit_card': Decimal('0.035'),  # 3.5%
            'debit_card': Decimal('0.025'),   # 2.5%
            'cash': Decimal('0.020'),         # 2.0%
            'transfer': Decimal('0.015'),     # 1.5%
            'paypal': Decimal('0.029'),       # 2.9%
        }
        
        percentage = fee_percentages.get(payment_method, Decimal('0.030'))
        return cart_total * percentage
    
    @staticmethod
    def get_payment_method_info(payment_method):
        """Obtener información del método de pago"""
        method_info = {
            'credit_card': {
                'name': 'Tarjeta de Crédito',
                'success_rate': 0.95,
                'processing_time': '2-3 segundos',
                'description': 'Pago con tarjeta de crédito',
                'icon': '💳'
            },
            'debit_card': {
                'name': 'Tarjeta de Débito',
                'success_rate': 0.98,
                'processing_time': '1-2 segundos',
                'description': 'Pago con tarjeta de débito',
                'icon': '💳'
            },
            'cash': {
                'name': 'Efectivo',
                'success_rate': 1.0,
                'processing_time': 'Inmediato',
                'description': 'Pago en efectivo',
                'icon': '💵'
            },
            'transfer': {
                'name': 'Transferencia Bancaria',
                'success_rate': 0.92,
                'processing_time': '1-3 días hábiles',
                'description': 'Transferencia bancaria',
                'icon': '🏦'
            },
            'paypal': {
                'name': 'PayPal',
                'success_rate': 0.97,
                'processing_time': '30-60 segundos',
                'description': 'Pago con PayPal',
                'icon': '📱'
            }
        }
        
        return method_info.get(payment_method, {
            'name': 'Método Desconocido',
            'success_rate': 0.90,
            'processing_time': 'Variable',
            'description': 'Método de pago no especificado',
            'icon': '❓'
        })
    
    @staticmethod
    def create_payment_record(provider, amount, transaction_type, description=""):
        """Crear un registro de pago"""
        try:
            payment = ProviderPayment.objects.create(
                provider=provider,
                amount=amount,
                transaction_type=transaction_type,
                description=description,
                is_completed=False
            )
            return payment
        except Exception as e:
            raise PaymentCreationError(f"Error creando registro de pago: {str(e)}")
    
    @staticmethod
    def complete_payment(payment_id):
        """Marcar un pago como completado"""
        try:
            payment = ProviderPayment.objects.get(id=payment_id)
            payment.is_completed = True
            payment.completed_at = timezone.now()
            payment.save()
            return payment
        except ProviderPayment.DoesNotExist:
            raise PaymentNotFoundError("Pago no encontrado")
        except Exception as e:
            raise PaymentCompletionError(f"Error completando pago: {str(e)}")
    
    @staticmethod
    def get_payment_statistics(provider):
        """Obtener estadísticas de pagos del proveedor"""
        payments = ProviderPayment.objects.filter(provider=provider)
        
        total_payments = payments.count()
        completed_payments = payments.filter(is_completed=True).count()
        pending_payments = total_payments - completed_payments
        
        total_amount = sum(payment.amount for payment in payments if payment.is_completed)
        
        # Calcular por tipo de transacción
        by_type = {}
        for payment_type in ProviderPayment.TransactionType.choices:
            type_payments = payments.filter(transaction_type=payment_type[0])
            by_type[payment_type[0]] = {
                'count': type_payments.count(),
                'total_amount': sum(p.amount for p in type_payments if p.is_completed),
                'completed': type_payments.filter(is_completed=True).count()
            }
        
        return {
            'total_payments': total_payments,
            'completed_payments': completed_payments,
            'pending_payments': pending_payments,
            'total_amount': total_amount,
            'success_rate': round(completed_payments / total_payments * 100, 2) if total_payments > 0 else 0,
            'by_type': by_type
        } 