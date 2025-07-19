from rest_framework import generics, permissions, status
from rest_framework.response import Response
from decimal import Decimal
import uuid
from django.db import transaction
from .models import ProviderPayment
from .serializers import ProviderPaymentSerializer, PaymentSimulationSerializer

class ProviderPaymentListView(generics.ListAPIView):
    serializer_class = ProviderPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ProviderPayment.objects.none()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset
        return ProviderPayment.objects.filter(
            provider__user=self.request.user
        ).order_by('-created_at')

class PaymentSimulationView(generics.GenericAPIView):
    serializer_class = PaymentSimulationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Lógica de simulación de pago
            return Response({
                'status': 'success',
                'transaction_id': f'sim_{uuid.uuid4().hex[:10]}',
                'amount': str(Decimal('100.00')),
                'currency': 'USD'
            }, status=status.HTTP_200_OK)