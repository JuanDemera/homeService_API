from django.urls import path
from .views import (
    ConsumerAppointmentListView,
    ConsumerCreateAppointmentView,
    ConsumerCancelAppointmentView,
    ProviderAppointmentListView,
    ProviderUpdateAppointmentView
)

urlpatterns = [
    # Consumer
    path('consumer/', ConsumerAppointmentListView.as_view(), name='consumer-appointments'),
    path('consumer/create/', ConsumerCreateAppointmentView.as_view(), name='consumer-create-appointment'),
    path('consumer/<int:pk>/cancel/', ConsumerCancelAppointmentView.as_view(), name='consumer-cancel-appointment'),

    # Provider
    path('provider/', ProviderAppointmentListView.as_view(), name='provider-appointments'),
    path('provider/<int:pk>/update/', ProviderUpdateAppointmentView.as_view(), name='provider-update-appointment'),
]
