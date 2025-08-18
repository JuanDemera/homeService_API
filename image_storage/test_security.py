from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

from .models import UserProfileImage, ServiceImage, ImageUploadLog
from providers.models import Provider
from providers.services.models import Service, Category

User = get_user_model()

def create_test_image_file(filename='test.jpg', width=200, height=200):
    """Crear un archivo de imagen de prueba"""
    image = Image.new('RGB', (width, height), color='red')
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)
    return SimpleUploadedFile(
        filename,
        buffer.getvalue(),
        content_type='image/jpeg'
    )

class SecurityPermissionsTest(APITestCase):
    """Tests específicos para verificar la seguridad y permisos"""
    
    def setUp(self):
        # Crear usuarios de prueba
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123',
            phone='1234567890'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123',
            phone='0987654321'
        )
        
        # Crear providers
        self.provider1 = Provider.objects.create(
            user=self.user1
        )
        
        self.provider2 = Provider.objects.create(
            user=self.user2
        )
        
        # Crear categoría
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Category Description'
        )
        
        # Crear servicios
        self.service1 = Service.objects.create(
            provider=self.provider1,
            title='Service 1',
            description='Test Service 1',
            category=self.category,
            price=100.00,
            duration_minutes=60
        )
        
        self.service2 = Service.objects.create(
            provider=self.provider2,
            title='Service 2',
            description='Test Service 2',
            category=self.category,
            price=200.00,
            duration_minutes=60
        )
        
        self.client = APIClient()
    
    def test_unauthenticated_user_cannot_access_profile_image(self):
        """Test: Usuario no autenticado no puede acceder a imagen de perfil"""
        url = reverse('image_storage:user-profile-image')
        
        # GET sin autenticación
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # POST sin autenticación
        image_file = create_test_image_file()
        response = self.client.post(url, {'image': image_file})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_cannot_modify_other_user_profile_image(self):
        """Test: Usuario no puede modificar imagen de perfil de otro usuario"""
        # Crear imagen de perfil para user1
        image_file = create_test_image_file()
        profile_image = UserProfileImage.objects.create(
            user=self.user1,
            image=image_file
        )
        
        # Autenticar como user2
        self.client.force_authenticate(user=self.user2)
        
        # Intentar modificar imagen de user1
        url = reverse('image_storage:user-profile-image')
        new_image = create_test_image_file('new.jpg')
        response = self.client.put(url, {'image': new_image})
        
        # Debería fallar porque user2 no puede modificar imagen de user1
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_can_only_access_own_profile_image(self):
        """Test: Usuario solo puede acceder a su propia imagen de perfil"""
        # Crear imagen de perfil para user1
        image_file = create_test_image_file()
        UserProfileImage.objects.create(
            user=self.user1,
            image=image_file
        )
        
        # Autenticar como user1
        self.client.force_authenticate(user=self.user1)
        
        # Debería poder acceder a su imagen
        url = reverse('image_storage:user-profile-image')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_image'])
    
    def test_provider_cannot_modify_other_provider_service_images(self):
        """Test: Provider no puede modificar imágenes de servicios de otro provider"""
        # Crear imagen de servicio para service1 (provider1)
        image_file = create_test_image_file()
        service_image = ServiceImage.objects.create(
            service=self.service1,
            image=image_file,
            is_primary=True
        )
        
        # Autenticar como user2 (provider2)
        self.client.force_authenticate(user=self.user2)
        
        # Intentar modificar imagen de service1
        url = reverse('image_storage:service-image-detail', kwargs={'pk': service_image.id})
        new_image = create_test_image_file('new_service.jpg')
        response = self.client.put(url, {'image': new_image})
        
        # Debería fallar porque provider2 no puede modificar service1
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_provider_can_modify_own_service_images(self):
        """Test: Provider puede modificar imágenes de sus propios servicios"""
        # Crear imagen de servicio para service1 (provider1)
        image_file = create_test_image_file()
        service_image = ServiceImage.objects.create(
            service=self.service1,
            image=image_file,
            is_primary=True
        )
        
        # Autenticar como user1 (provider1)
        self.client.force_authenticate(user=self.user1)
        
        # Debería poder modificar su imagen
        url = reverse('image_storage:service-image-detail', kwargs={'pk': service_image.id})
        new_image = create_test_image_file('new_service.jpg')
        response = self.client.put(url, {'image': new_image})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_provider_cannot_upload_to_other_provider_service(self):
        """Test: Provider no puede subir imágenes a servicios de otro provider"""
        # Autenticar como user2 (provider2)
        self.client.force_authenticate(user=self.user2)
        
        # Intentar subir imagen a service1 (pertenece a provider1)
        url = reverse('image_storage:service-images-list', kwargs={'service_id': self.service1.id})
        image_file = create_test_image_file()
        response = self.client.post(url, {'image': image_file})
        
        # Debería fallar
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_provider_can_upload_to_own_service(self):
        """Test: Provider puede subir imágenes a sus propios servicios"""
        # Autenticar como user1 (provider1)
        self.client.force_authenticate(user=self.user1)
        
        # Subir imagen a service1 (pertenece a provider1)
        url = reverse('image_storage:service-images-list', kwargs={'service_id': self.service1.id})
        image_file = create_test_image_file()
        response = self.client.post(url, {'image': image_file})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_bulk_upload_permissions(self):
        """Test: Solo el propietario puede hacer subida múltiple"""
        # Autenticar como user2 (provider2)
        self.client.force_authenticate(user=self.user2)
        
        # Intentar subida múltiple a service1 (pertenece a provider1)
        url = reverse('image_storage:bulk-upload')
        image_files = [create_test_image_file(f'test{i}.jpg') for i in range(2)]
        
        data = {
            'service_id': self.service1.id,
            'images': image_files
        }
        
        response = self.client.post(url, data, format='multipart')
        
        # Debería fallar
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_set_primary_image_permissions(self):
        """Test: Solo el propietario puede establecer imagen principal"""
        # Crear imagen de servicio para service1
        image_file = create_test_image_file()
        service_image = ServiceImage.objects.create(
            service=self.service1,
            image=image_file,
            is_primary=False
        )
        
        # Autenticar como user2 (provider2)
        self.client.force_authenticate(user=self.user2)
        
        # Intentar establecer como principal
        url = reverse('image_storage:set-primary-image', kwargs={'image_id': service_image.id})
        response = self.client.post(url)
        
        # Debería fallar
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_service_summary_permissions(self):
        """Test: Solo el propietario puede ver resumen de sus servicios"""
        # Autenticar como user2 (provider2)
        self.client.force_authenticate(user=self.user2)
        
        # Intentar ver resumen de service1 (pertenece a provider1)
        url = reverse('image_storage:service-images-summary', kwargs={'service_id': self.service1.id})
        response = self.client.get(url)
        
        # Debería fallar
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_logs_permissions(self):
        """Test: Usuario solo puede ver sus propios logs"""
        # Crear logs para user1
        ImageUploadLog.objects.create(
            user=self.user1,
            upload_type='profile',
            file_name='test.jpg',
            file_size=1024,
            success=True
        )
        
        # Crear logs para user2
        ImageUploadLog.objects.create(
            user=self.user2,
            upload_type='profile',
            file_name='test2.jpg',
            file_size=2048,
            success=True
        )
        
        # Autenticar como user1
        self.client.force_authenticate(user=self.user1)
        
        # Ver logs de user1
        url = reverse('image_storage:upload-logs')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debería ver sus propios logs
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user1.id)

class TokenSecurityTest(APITestCase):
    """Tests para verificar la seguridad de tokens"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            phone='1234567890'
        )
        self.client = APIClient()
    
    def test_invalid_token_denied(self):
        """Test: Token inválido es rechazado"""
        url = reverse('image_storage:user-profile-image')
        
        # Token inválido
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_expired_token_denied(self):
        """Test: Token expirado es rechazado"""
        # Este test requeriría configurar un token expirado
        # Se puede implementar con mock o configuración específica
        pass
    
    def test_no_token_denied(self):
        """Test: Request sin token es rechazado"""
        url = reverse('image_storage:user-profile-image')
        
        # Sin token
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class FileValidationSecurityTest(APITestCase):
    """Tests para verificar la validación de archivos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            phone='1234567890'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_invalid_file_type_rejected(self):
        """Test: Tipo de archivo inválido es rechazado"""
        url = reverse('image_storage:user-profile-image')
        
        # Archivo de texto en lugar de imagen
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'This is not an image',
            content_type='text/plain'
        )
        
        response = self.client.post(url, {'image': invalid_file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_large_file_rejected(self):
        """Test: Archivo muy grande es rechazado"""
        url = reverse('image_storage:user-profile-image')
        
        # Archivo grande (6MB)
        large_file = SimpleUploadedFile(
            'large.jpg',
            b'x' * (6 * 1024 * 1024),
            content_type='image/jpeg'
        )
        
        response = self.client.post(url, {'image': large_file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_malicious_file_rejected(self):
        """Test: Archivo malicioso es rechazado"""
        url = reverse('image_storage:user-profile-image')
        
        # Archivo con extensión .jpg pero contenido malicioso
        malicious_file = SimpleUploadedFile(
            'malicious.jpg',
            b'<script>alert("xss")</script>',
            content_type='image/jpeg'
        )
        
        response = self.client.post(url, {'image': malicious_file})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 