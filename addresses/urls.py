from django.urls import path
from . import views

app_name = 'addresses'

urlpatterns = [
    # Gestión básica de direcciones
    path('', views.AddressListView.as_view(), name='address-list'),
    path('<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    
    # Dirección por defecto
    path('default/', views.AddressDefaultView.as_view(), name='address-default'),
    path('<int:address_id>/set-default/', views.set_default_address, name='set-default-address'),
    
    # Geolocalización
    path('geolocation/', views.AddressGeolocationView.as_view(), name='address-geolocation'),
    
    # Sugerencias de direcciones
    path('suggestions/', views.address_suggestions, name='address-suggestions'),
    
    # Resumen de direcciones
    path('summary/', views.address_summary, name='address-summary'),
] 