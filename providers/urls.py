from django.urls import path
from .views import (
    ProviderRegisterView,
    ProviderVerificationRequestView,
    ProviderVerificationAdminView
)

urlpatterns = [
    
    path('register/', ProviderRegisterView.as_view(), name='provider-register'),
    
    path('me/verify/', ProviderVerificationRequestView.as_view(), name='provider-verification-request'),
    
    path('<str:phone>/verify/', ProviderVerificationAdminView.as_view(), name='provider-admin-verify'),
]