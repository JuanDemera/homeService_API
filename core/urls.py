from django.urls import path
from .views import CustomTokenObtainPairView
from .views import test_connection

app_name = 'core'

urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/ping/', test_connection),
]
