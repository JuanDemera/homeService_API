from django.urls import path
from .views import (
    CategoryListView,
    CategoryCreateView,
    ServiceListView,
    ServiceCreateView,
    ServiceUpdateView,
    ProviderMyServicesView,
    AdminServiceCreateView
)

urlpatterns = [
    # Público / Consumer
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('services/', ServiceListView.as_view(), name='service-list'),

    # Provider
    path('my-services/', ProviderMyServicesView.as_view(), name='provider-my-services'),
    path('services/create/', ServiceCreateView.as_view(), name='service-create'),
    path('services/<int:id>/edit/', ServiceUpdateView.as_view(), name='service-update'),

    # Admin
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('services/admin-create/', AdminServiceCreateView.as_view(), name='admin-service-create'),
]
