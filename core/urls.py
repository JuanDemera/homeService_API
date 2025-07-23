from django.urls import path
from .views import CustomTokenView
from .views import test_connection

app_name = 'core'

urlpatterns = [
    path('token/', CustomTokenView.as_view(), name='token_obtain_pair'),
    path('api/ping/', test_connection),
]
