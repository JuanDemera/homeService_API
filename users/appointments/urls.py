from django.urls import path
from .views import (
    ConsumerAppointmentListView,
    ConsumerCreateAppointmentView,
    ConsumerAppointmentDetailView,
    ConsumerUpdateAppointmentView,
    ConsumerCancelAppointmentView,
    MarkAppointmentAsPaidView,
    ProviderAppointmentListView,
    ProviderAppointmentDetailView,
    ProviderUpdateAppointmentView,
    ProviderServiceAppointmentsView,
    appointment_statistics,
    provider_dashboard,
    check_appointment_availability
)

urlpatterns = [
    # Consumer
    path('consumer/', ConsumerAppointmentListView.as_view(), name='consumer-appointments'),
    path('consumer/create/', ConsumerCreateAppointmentView.as_view(), name='consumer-create-appointment'),
    path('consumer/<int:pk>/', ConsumerAppointmentDetailView.as_view(), name='consumer-appointment-detail'),
    path('consumer/<int:pk>/update/', ConsumerUpdateAppointmentView.as_view(), name='consumer-update-appointment'),
    path('consumer/<int:pk>/cancel/', ConsumerCancelAppointmentView.as_view(), name='consumer-cancel-appointment'),
    path('consumer/<int:pk>/mark-paid/', MarkAppointmentAsPaidView.as_view(), name='consumer-mark-paid'),

    # Provider
    path('provider/', ProviderAppointmentListView.as_view(), name='provider-appointments'),
    path('provider/<int:pk>/', ProviderAppointmentDetailView.as_view(), name='provider-appointment-detail'),
    path('provider/<int:pk>/update/', ProviderUpdateAppointmentView.as_view(), name='provider-update-appointment'),
    path('provider/service/<int:service_id>/', ProviderServiceAppointmentsView.as_view(), name='provider-service-appointments'),
    path('provider/dashboard/', provider_dashboard, name='provider-dashboard'),

    # Generales
    path('statistics/', appointment_statistics, name='appointment-statistics'),
    path('availability/', check_appointment_availability, name='check-availability'),
]
