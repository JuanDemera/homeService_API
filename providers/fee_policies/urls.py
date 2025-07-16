from django.urls import path
from .views import (
    FeePolicyListView,
    FeePolicyDetailView,
    CurrentFeePolicyView
)

urlpatterns = [
    path('policies/', FeePolicyListView.as_view(), name='fee-policy-list'),
    path('policies/<int:pk>/', FeePolicyDetailView.as_view(), name='fee-policy-detail'),
    path('policies/current/', CurrentFeePolicyView.as_view(), name='current-fee-policies'),
]