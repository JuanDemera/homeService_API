from django.urls import path
from .views import (
    GuestAccessView, SendOTPView, VerifyOTPView, RegisterConsumerView,
    ConsumerProfileView, UpdateConsumerProfileView, ChangePasswordView
)

urlpatterns = [
    path('guest/', GuestAccessView.as_view(), name='guest_access'),
    path('otp/send/', SendOTPView.as_view(), name='send_otp'),
    path('otp/verify/', VerifyOTPView.as_view(), name='verify_otp'),
    path('register/consumer/', RegisterConsumerView.as_view(), name='register_consumer'),
    
    # Endpoints para perfil de usuario consumer
    path('me/profile/', ConsumerProfileView.as_view(), name='consumer_profile'),
    path('me/profile/update/', UpdateConsumerProfileView.as_view(), name='update_consumer_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
] 