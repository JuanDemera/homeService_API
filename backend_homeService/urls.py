"""
URL configuration for backend_homeService project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from core.views import CustomTokenView
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.http import HttpResponse


urlpatterns = [
    path('', lambda request: HttpResponse("¡Bienvenido a HomeServiceAPI!")),
    path('admin/', admin.site.urls),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Core (autenticación)
    path('api/auth/', include('core.urls')),
    
    # Users
    path('api/users/', include('users.urls')),
    path('api/carts/', include('users.carts.urls')),
    
    # Providers
    path('api/providers/', include('providers.urls')),
    path('api/services/', include('providers.services.urls')),
    path('api/payments/', include('providers.payments.urls')),
]


   
    
