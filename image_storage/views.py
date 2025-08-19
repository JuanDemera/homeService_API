from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .models import UserProfileImage, ServiceImage, ImageUploadLog
from .serializers import (
    UserProfileImageSerializer, 
    ServiceImageSerializer, 
    ImageUploadLogSerializer,
    BulkImageUploadSerializer
)
from .permissions import IsProfileOwner, IsServiceOwner, CanManageServiceImages
from providers.services.models import Service
import logging

# Swagger (drf_yasg)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

class UserProfileImageView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para gestionar la imagen de perfil del usuario autenticado"""
    serializer_class = UserProfileImageSerializer
    permission_classes = [IsProfileOwner]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self):
        """Obtener la imagen de perfil del usuario actual"""
        try:
            return UserProfileImage.objects.get(user=self.request.user)
        except UserProfileImage.DoesNotExist:
            return None
    
    def get(self, request, *args, **kwargs):
        """Obtener la imagen de perfil del usuario"""
        instance = self.get_object()
        if not instance or not instance.image:
            return Response({
                'message': 'No hay imagen de perfil configurada',
                'has_image': False,
                'image_url': None,
                'file_size': 0
            }, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(instance)
        return Response({
            **serializer.data,
            'has_image': True
        })
    
    @swagger_auto_schema(auto_schema=None)
    def post(self, request, *args, **kwargs):
        """Crear o actualizar la imagen de perfil"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return Response({
            **serializer.data,
            'has_image': True
        }, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        """Actualizar la imagen de perfil"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return Response({
            **serializer.data,
            'has_image': True
        }, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(auto_schema=None)
    def patch(self, request, *args, **kwargs):
        """Actualizar parcialmente la imagen de perfil"""
        return self.partial_update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Eliminar la imagen de perfil"""
        instance = self.get_object()
        if instance and instance.image:
            instance.delete()
            return Response({
                'message': 'Imagen de perfil eliminada correctamente'
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({
            'message': 'No hay imagen de perfil para eliminar'
        }, status=status.HTTP_404_NOT_FOUND)

class ServiceImageListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear imágenes de servicios"""
    serializer_class = ServiceImageSerializer
    permission_classes = [CanManageServiceImages]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Obtener imágenes del servicio especificado"""
        if getattr(self, 'swagger_fake_view', False):
            return ServiceImage.objects.none()
        service_id = self.kwargs.get('service_id')
        return ServiceImage.objects.filter(service_id=service_id, is_active=True)
    
    def list(self, request, *args, **kwargs):
        """Listar imágenes del servicio con manejo de caso vacío"""
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({
                'message': 'No hay imágenes configuradas para este servicio',
                'total_images': 0,
                'images': [],
                'has_images': False
            }, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'total_images': queryset.count(),
            'images': serializer.data,
            'has_images': True
        })
    
    def get_serializer_context(self):
        """Agregar el service_id al contexto del serializer"""
        context = super().get_serializer_context()
        context['service_id'] = self.kwargs.get('service_id')
        return context
    
    @swagger_auto_schema(auto_schema=None)
    def post(self, request, *args, **kwargs):
        """Crear imagen de servicio (Swagger deshabilitado)"""
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(auto_schema=None)
    def perform_create(self, serializer):
        """Crear la imagen y verificar permisos"""
        service_id = self.kwargs.get('service_id')
        service = get_object_or_404(Service, id=service_id)
        
        # Verificar que el usuario es el propietario del servicio
        if service.provider.user != self.request.user:
            raise PermissionDenied("No tienes permisos para subir imágenes a este servicio.")
        
        serializer.save()

class ServiceImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para gestionar una imagen específica de servicio"""
    serializer_class = ServiceImageSerializer
    permission_classes = [IsServiceOwner]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Obtener la imagen específica"""
        if getattr(self, 'swagger_fake_view', False):
            return ServiceImage.objects.none()
        return ServiceImage.objects.filter(is_active=True)
    
    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        """Actualizar imagen de servicio (Swagger deshabilitado)"""
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(auto_schema=None)
    def patch(self, request, *args, **kwargs):
        """Actualizar parcialmente imagen de servicio (Swagger deshabilitado)"""
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(auto_schema=None)
    def perform_update(self, serializer):
        """Actualizar la imagen y verificar permisos"""
        instance = self.get_object()
        service = instance.service
        
        # Verificar que el usuario es el propietario del servicio
        if service.provider.user != self.request.user:
            raise PermissionDenied("No tienes permisos para modificar imágenes de este servicio.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Eliminar la imagen y verificar permisos"""
        service = instance.service
        
        # Verificar que el usuario es el propietario del servicio
        if service.provider.user != self.request.user:
            raise PermissionDenied("No tienes permisos para eliminar imágenes de este servicio.")
        
        instance.delete()

class BulkImageUploadView(generics.CreateAPIView):
    """Vista para subida múltiple de imágenes de servicios"""
    serializer_class = BulkImageUploadSerializer
    permission_classes = [CanManageServiceImages]
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(auto_schema=None)
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Crear múltiples imágenes de servicio"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service_id = serializer.validated_data['service_id']
        images = serializer.validated_data['images']
        
        # Verificar permisos
        service = get_object_or_404(Service, id=service_id)
        if service.provider.user != request.user:
            raise PermissionDenied("No tienes permisos para subir imágenes a este servicio.")
        
        created_images = []
        errors = []
        
        for i, image in enumerate(images):
            try:
                # Crear la imagen de servicio
                service_image = ServiceImage.objects.create(
                    service=service,
                    image=image,
                    is_primary=(i == 0)  # La primera imagen será la principal
                )
                
                # Registrar en el log
                ImageUploadLog.objects.create(
                    user=request.user,
                    upload_type='service',
                    file_name=service_image.image.name,
                    file_size=service_image.image.size,
                    success=True
                )
                
                created_images.append(ServiceImageSerializer(service_image, context={'request': request}).data)
                
            except Exception as e:
                logger.error(f"Error al subir imagen {i+1}: {str(e)}")
                errors.append(f"Error en imagen {i+1}: {str(e)}")
                
                # Registrar error en el log
                ImageUploadLog.objects.create(
                    user=request.user,
                    upload_type='service',
                    file_name=image.name if hasattr(image, 'name') else f'image_{i+1}',
                    file_size=image.size if hasattr(image, 'size') else 0,
                    success=False,
                    error_message=str(e)
                )
        
        if errors:
            return Response({
                'message': 'Algunas imágenes no se pudieron subir',
                'created_images': created_images,
                'errors': errors
            }, status=status.HTTP_207_MULTI_STATUS)
        
        return Response({
            'message': f'{len(created_images)} imágenes subidas correctamente',
            'created_images': created_images
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(auto_schema=None)
    def post(self, request, *args, **kwargs):
        """Delegar POST a create con Swagger deshabilitado"""
        return self.create(request, *args, **kwargs)

class ImageUploadLogListView(generics.ListAPIView):
    """Vista para listar logs de subida de imágenes"""
    serializer_class = ImageUploadLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Obtener logs del usuario actual"""
        if getattr(self, 'swagger_fake_view', False):
            return ImageUploadLog.objects.none()
        return ImageUploadLog.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_primary_image(request, image_id):
    """Establecer una imagen como principal para un servicio"""
    try:
        image = get_object_or_404(ServiceImage, id=image_id, is_active=True)
        
        # Verificar permisos
        if image.service.provider.user != request.user:
            raise PermissionDenied("No tienes permisos para modificar este servicio.")
        
        # Marcar como principal
        image.is_primary = True
        image.save()
        
        return Response({
            'message': 'Imagen establecida como principal correctamente',
            'image_id': image.id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def service_images_summary(request, service_id):
    """Obtener resumen de imágenes de un servicio"""
    try:
        service = get_object_or_404(Service, id=service_id)
        
        # Verificar permisos
        if service.provider.user != request.user:
            raise PermissionDenied("No tienes permisos para ver este servicio.")
        
        images = ServiceImage.objects.filter(service=service, is_active=True)
        primary_image = images.filter(is_primary=True).first()
        
        if not images.exists():
            return Response({
                'service_id': service_id,
                'service_name': service.title,
                'total_images': 0,
                'primary_image': None,
                'all_images': [],
                'has_images': False,
                'message': 'No hay imágenes configuradas para este servicio'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'service_id': service_id,
            'service_name': service.title,
            'total_images': images.count(),
            'primary_image': ServiceImageSerializer(primary_image, context={'request': request}).data if primary_image else None,
            'all_images': ServiceImageSerializer(images, context={'request': request}, many=True).data,
            'has_images': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
