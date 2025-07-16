from django.urls import path
from .views import GuestAccessView, SendOTPView, VerifyOTPView, RegisterConsumerView

urlpatterns = [
    path('guest/', GuestAccessView.as_view(), name='guest_access'),
    path('otp/send/', SendOTPView.as_view(), name='send_otp'),
    path('otp/verify/', VerifyOTPView.as_view(), name='verify_otp'),
    path('register/consumer/', RegisterConsumerView.as_view(), name='register_consumer'),
]
