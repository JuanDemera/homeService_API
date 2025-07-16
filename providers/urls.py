from django.urls import path
from .views import ProviderDetailView, ProviderRegisterView

from .views import (
    ProviderDetailView,
    ProviderRegisterView,
    ProviderVerificationView,
    ProviderAvailabilityView
)

urlpatterns = [
    path('me/', ProviderDetailView.as_view(), name='provider-detail'),
    path('register/', ProviderRegisterView.as_view(), name='provider-register'),
    path('<str:username>/verify/', ProviderVerificationView.as_view(), name='provider-verification'),
    path('<str:username>/availability/', ProviderAvailabilityView.as_view(), name='provider-availability'),
]