from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ProviderPayment
from .serializers import ProviderPaymentSerializer, PaymentSimulationSerializer
from django.db import transaction

class ProviderPaymentListView(generics.ListAPIView):
    serializer_class = ProviderPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProviderPayment.objects.filter(
            provider__user=self.request.user
        ).order_by('-created_at')

class PaymentSimulationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentSimulationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Simular proceso de pago
        with transaction.atomic():
            # Aquí iría la lógica real de pago
            # Por ahora solo simulamos éxito
            
            return Response({
                'status': 'success',
                'message': 'Payment simulated successfully',
                'transaction_id': 'simulated_' + str(uuid.uuid4()),
                'amount': 100.00  # Valor simulado
            }, status=status.HTTP_200_OK)