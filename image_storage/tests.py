from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from PIL import Image
from io import BytesIO
import tempfile
import os
import shutil

from .models import UserProfileImage, ServiceImage, ImageUploadLog
from providers.models import Provider, Service

User = get_user_model()

def create_test_image(width=200, height=200, format='JPEG'):
    """Crear una imagen de prueba"""
    image = Image.new('RGB', (width, height), color='red')
    buffer = BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer

def create_test_image_file(filename='test.jpg', width=200, height=200):
    """Crear un archivo de imagen de prueba"""
    image_buffer = create_test_image(width, height)
    return SimpleUploadedFile(
        filename,
        image_buffer.getvalue(),
        content_type='image/jpeg'
    )

class ImageStorageModelsTest(TestCase):
    """Tests para los modelos de almacenamiento de imágenes"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = Provider.objects.create(
            user=self.user,
            business_name='Test Provider',
            phone='1234567890'
        )
        
        self.service = Service.objects.create(
            provider=self.provider,
            name='Test Service',
            description='Test Description',
            price=100.00
        )
    
    def test_user_profile_image_creation(self):
        """Test crear imagen de perfil de usuario"""
        image_file = create_test_image_file()
        
        profile_image = UserProfileImage.objects.create(
            user=self.user,
            image=image_file
        )
        
        self.assertEqual(profile_image.user, self.user)
        self.assertTrue(profile_image.image)
        self.assertTrue(profile_image.is_active)
    
    def test_service_image_creation(self):
        """Test crear imagen de servicio"""
        image_file = create_test_image_file()
        
        service_image = ServiceImage.objects.create(
            service=self.service,
            image=image_file,
            is_primary=True
        )
        
        self.assertEqual(service_image.service, self.service)
        self.assertTrue(service_image.image)
        self.assertTrue(service_image.is_primary)
        self.assertTrue(service_image.is_active)
    
    def test_service_image_primary_logic(self):
        """Test lógica de imagen principal"""
        # Crear primera imagen
        image1_file = create_test_image_file('test1.jpg')
        service_image1 = ServiceImage.objects.create(
            service=self.service,
            image=image1_file,
            is_primary=True
        )
        
        # Crear segunda imagen como principal
        image2_file = create_test_image_file('test2.jpg')
        service_image2 = ServiceImage.objects.create(
            service=self.service,
            image=image2_file,
            is_primary=True
        )
        
        # Verificar que solo la segunda es principal
        service_image1.refresh_from_db()
        self.assertFalse(service_image1.is_primary)
        self.assertTrue(service_image2.is_primary)
    
    def test_image_upload_log_creation(self):
        """Test crear log de subida de imagen"""
        log = ImageUploadLog.objects.create(
            user=self.user,
            upload_type='profile',
            file_name='test.jpg',
            file_size=1024,
            success=True
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.upload_type, 'profile')
        self.assertTrue(log.success)

class ImageStorageAPITest(APITestCase):
    """Tests para las APIs de almacenamiento de imágenes"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = Provider.objects.create(
            user=self.user,
            business_name='Test Provider',
            phone='1234567890'
        )
        
        self.service = Service.objects.create(
            provider=self.provider,
            name='Test Service',
            description='Test Description',
            price=100.00
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_upload_profile_image(self):
        """Test subir imagen de perfil"""
        url = reverse('image_storage:user-profile-image')
        image_file = create_test_image_file()
        
        data = {'image': image_file}
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserProfileImage.objects.filter(user=self.user).exists())
    
    def test_get_profile_image(self):
        """Test obtener imagen de perfil"""
        # Crear imagen de perfil
        image_file = create_test_image_file()
        UserProfileImage.objects.create(user=self.user, image=image_file)
        
        url = reverse('image_storage:user-profile-image')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_image'])
    
    def test_upload_service_image(self):
        """Test subir imagen de servicio"""
        url = reverse('image_storage:service-images-list', kwargs={'service_id': self.service.id})
        image_file = create_test_image_file()
        
        data = {'image': image_file}
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ServiceImage.objects.filter(service=self.service).exists())
    
    def test_bulk_upload_service_images(self):
        """Test subida múltiple de imágenes de servicio"""
        url = reverse('image_storage:bulk-upload')
        
        # Crear múltiples archivos de imagen
        image_files = [
            create_test_image_file(f'test{i}.jpg') for i in range(3)
        ]
        
        data = {
            'service_id': self.service.id,
            'images': image_files
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ServiceImage.objects.filter(service=self.service).count(), 3)
    
    def test_set_primary_image(self):
        """Test establecer imagen como principal"""
        # Crear imagen de servicio
        image_file = create_test_image_file()
        service_image = ServiceImage.objects.create(
            service=self.service,
            image=image_file,
            is_primary=False
        )
        
        url = reverse('image_storage:set-primary-image', kwargs={'image_id': service_image.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_image.refresh_from_db()
        self.assertTrue(service_image.is_primary)
    
    def test_service_images_summary(self):
        """Test obtener resumen de imágenes de servicio"""
        # Crear imágenes de servicio
        for i in range(3):
            image_file = create_test_image_file(f'test{i}.jpg')
            ServiceImage.objects.create(
                service=self.service,
                image=image_file,
                is_primary=(i == 0)
            )
        
        url = reverse('image_storage:service-images-summary', kwargs={'service_id': self.service.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_images'], 3)
        self.assertIsNotNone(response.data['primary_image'])
    
    def test_upload_logs(self):
        """Test obtener logs de subida"""
        # Crear algunos logs
        ImageUploadLog.objects.create(
            user=self.user,
            upload_type='profile',
            file_name='test.jpg',
            file_size=1024,
            success=True
        )
        
        url = reverse('image_storage:upload-logs')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ImageValidationTest(TestCase):
    """Tests para validación de imágenes"""
    
    def test_valid_image_validation(self):
        """Test validación de imagen válida"""
        from .services import ImageValidationService
        
        image_file = create_test_image_file()
        result = ImageValidationService.validate_profile_image(image_file)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_large_image_validation(self):
        """Test validación de imagen muy grande"""
        from .services import ImageValidationService
        
        # Crear imagen grande (simular archivo grande)
        large_image = SimpleUploadedFile(
            'large.jpg',
            b'x' * (6 * 1024 * 1024),  # 6MB
            content_type='image/jpeg'
        )
        
        result = ImageValidationService.validate_profile_image(large_image)
        
        self.assertFalse(result['is_valid'])
        self.assertTrue(any('demasiado grande' in error for error in result['errors']))
    
    def test_invalid_format_validation(self):
        """Test validación de formato inválido"""
        from .services import ImageValidationService
        
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'not an image',
            content_type='text/plain'
        )
        
        result = ImageValidationService.validate_profile_image(invalid_file)
        
        self.assertFalse(result['is_valid'])
        self.assertTrue(any('Formato no permitido' in error for error in result['errors']))

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImageProcessingTest(TestCase):
    """Tests para procesamiento de imágenes"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_image_resize(self):
        """Test redimensionar imagen"""
        from .services import ImageProcessingService
        
        # Crear imagen grande
        large_image = create_test_image(800, 600)
        
        # Redimensionar
        resized = ImageProcessingService.resize_image(large_image, max_width=400, max_height=300)
        
        # Verificar dimensiones
        img = Image.open(resized)
        self.assertLessEqual(img.size[0], 400)
        self.assertLessEqual(img.size[1], 300)
    
    def test_thumbnail_creation(self):
        """Test crear miniatura"""
        from .services import ImageProcessingService
        
        original_image = create_test_image(500, 500)
        thumbnail = ImageProcessingService.create_thumbnail(original_image, size=(100, 100))
        
        img = Image.open(thumbnail)
        self.assertLessEqual(img.size[0], 100)
        self.assertLessEqual(img.size[1], 100)
