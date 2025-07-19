from django.urls import path
from .views import ProviderPaymentListView, PaymentSimulationView

urlpatterns = [
    path('history/', ProviderPaymentListView.as_view(), name='payment-history'),
    path('simulate/', PaymentSimulationView.as_view(), name='payment-simulate'),
]