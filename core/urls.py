from django.urls import path
from .views import CustomTokenView

app_name = 'core'

urlpatterns = [
    path('token/', CustomTokenView.as_view(), name='token_obtain_pair'),
]