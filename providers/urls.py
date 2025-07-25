from django.urls import path
from .views import (
    ProviderRegisterView,
    ProviderVerificationRequestView,
    ProviderVerificationAdminView,
    ProviderUpdateView,
    ProviderListView,
    ProviderProfileView,
    ProviderDetailAdminView
)

urlpatterns = [
    path('register/', ProviderRegisterView.as_view(), name='provider-register'),
    path('me/verify/', ProviderVerificationRequestView.as_view(), name='provider-verification-request'),
    path('<str:phone>/verify/', ProviderVerificationAdminView.as_view(), name='provider-admin-verify'),
    path('providers/<int:id>/edit/', ProviderUpdateView.as_view(), name='provider-edit'),
    path('providers/', ProviderListView.as_view(), name='provider-list'),
    path('me/profile/', ProviderProfileView.as_view(), name='provider-profile'),
    path('providers/<int:id>/', ProviderDetailAdminView.as_view(), name='provider-detail-admin'),
]
