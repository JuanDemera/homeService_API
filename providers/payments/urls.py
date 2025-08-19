from django.urls import path
from .views import ProviderPaymentListView, PaymentSimulationView, PaymentHistoryView

urlpatterns = [
    path('history/', PaymentHistoryView.as_view(), name='payment-history'),
    path('simulate/', PaymentSimulationView.as_view(), name='payment-simulate'),
    path('list/', ProviderPaymentListView.as_view(), name='payment-list'),
]