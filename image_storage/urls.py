from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'image_storage'

urlpatterns = [
    # Imágenes de perfil de usuarios
    path('profile/', views.UserProfileImageView.as_view(), name='user-profile-image'),
    
    # Imágenes de servicios
    path('services/<int:service_id>/images/', views.ServiceImageListCreateView.as_view(), name='service-images-list'),
    path('services/<int:service_id>/images/summary/', views.service_images_summary, name='service-images-summary'),
    path('services/images/<int:pk>/', views.ServiceImageDetailView.as_view(), name='service-image-detail'),
    path('services/images/<int:image_id>/set-primary/', views.set_primary_image, name='set-primary-image'),
    
    # Subida múltiple de imágenes
    path('services/bulk-upload/', views.BulkImageUploadView.as_view(), name='bulk-upload'),
    
    # Logs de subida
    path('logs/', views.ImageUploadLogListView.as_view(), name='upload-logs'),
] 