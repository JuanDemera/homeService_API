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

class NoImagesHandlingTest(APITestCase):
    """Tests para verificar el manejo de casos sin imágenes"""
    
    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            phone='1234567890'
        )
        
        # Crear provider
        self.provider = Provider.objects.create(
            user=self.user
        )
        
        # Crear categoría
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Category Description'
        )
        
        # Crear servicio
        self.service = Service.objects.create(
            provider=self.provider,
            title='Test Service',
            description='Test Description',
            category=self.category,
            price=100.00,
            duration_minutes=60
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_user_without_profile_image(self):
        """Test: Usuario sin imagen de perfil"""
        url = reverse('image_storage:user-profile-image')
        
        # GET sin imagen de perfil
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_image'])
        self.assertIsNone(response.data['image_url'])
        self.assertEqual(response.data['file_size'], 0)
        self.assertIn('No hay imagen de perfil configurada', response.data['message'])
    
    def test_delete_nonexistent_profile_image(self):
        """Test: Eliminar imagen de perfil que no existe"""
        url = reverse('image_storage:user-profile-image')
        
        # DELETE sin imagen de perfil
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No hay imagen de perfil para eliminar', response.data['message'])
    
    def test_service_without_images(self):
        """Test: Servicio sin imágenes"""
        url = reverse('image_storage:service-images-list', kwargs={'service_id': self.service.id})
        
        # GET sin imágenes
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_images'])
        self.assertEqual(response.data['total_images'], 0)
        self.assertEqual(response.data['images'], [])
        self.assertIn('No hay imágenes configuradas', response.data['message'])
    
    def test_service_summary_without_images(self):
        """Test: Resumen de servicio sin imágenes"""
        url = reverse('image_storage:service-images-summary', kwargs={'service_id': self.service.id})
        
        # GET sin imágenes
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_images'])
        self.assertEqual(response.data['total_images'], 0)
        self.assertIsNone(response.data['primary_image'])
        self.assertEqual(response.data['all_images'], [])
        self.assertEqual(response.data['service_name'], 'Test Service')
        self.assertIn('No hay imágenes configuradas', response.data['message'])
    
    def test_upload_first_profile_image(self):
        """Test: Subir primera imagen de perfil"""
        url = reverse('image_storage:user-profile-image')
        image_file = create_test_image_file()
        
        # POST primera imagen
        response = self.client.post(url, {'image': image_file})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['has_image'])
        self.assertIsNotNone(response.data['image_url'])
        self.assertGreater(response.data['file_size'], 0)
        
        # Verificar que se creó el registro
        self.assertTrue(UserProfileImage.objects.filter(user=self.user).exists())
    
    def test_upload_first_service_image(self):
        """Test: Subir primera imagen de servicio"""
        url = reverse('image_storage:service-images-list', kwargs={'service_id': self.service.id})
        image_file = create_test_image_file()
        
        # POST primera imagen
        response = self.client.post(url, {'image': image_file})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['image_url'])
        self.assertGreater(response.data['file_size'], 0)
        self.assertTrue(response.data['is_primary'])  # Primera imagen debe ser principal
        
        # Verificar que se creó el registro
        self.assertTrue(ServiceImage.objects.filter(service=self.service).exists())
    
    def test_update_profile_image(self):
        """Test: Actualizar imagen de perfil existente"""
        # Crear imagen inicial
        initial_image = create_test_image_file('initial.jpg')
        profile_image = UserProfileImage.objects.create(
            user=self.user,
            image=initial_image
        )
        
        url = reverse('image_storage:user-profile-image')
        new_image = create_test_image_file('new.jpg')
        
        # PUT nueva imagen
        response = self.client.put(url, {'image': new_image})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_image'])
        self.assertIsNotNone(response.data['image_url'])
        
        # Verificar que se actualizó
        profile_image.refresh_from_db()
        self.assertIsNotNone(profile_image.image)
        self.assertNotIn('initial.jpg', profile_image.image.name)
    
    def test_bulk_upload_to_empty_service(self):
        """Test: Subida múltiple a servicio sin imágenes"""
        url = reverse('image_storage:bulk-upload')
        image_files = [create_test_image_file(f'test{i}.jpg') for i in range(2)]
        
        data = {
            'service_id': self.service.id,
            'images': image_files
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['created_images']), 2)
        
        # Verificar que se crearon los registros
        service_images = ServiceImage.objects.filter(service=self.service)
        self.assertEqual(service_images.count(), 2)
        
        # Verificar que la primera es principal
        primary_image = service_images.filter(is_primary=True).first()
        self.assertIsNotNone(primary_image)
    
    def test_logs_without_uploads(self):
        """Test: Logs sin subidas previas"""
        url = reverse('image_storage:upload-logs')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_logs_after_upload(self):
        """Test: Logs después de subir imagen"""
        # Subir imagen
        url = reverse('image_storage:user-profile-image')
        image_file = create_test_image_file()
        self.client.post(url, {'image': image_file})
        
        # Verificar logs
        logs_url = reverse('image_storage:upload-logs')
        response = self.client.get(logs_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['upload_type'], 'profile')
        self.assertTrue(response.data[0]['success'])

class EdgeCasesTest(APITestCase):
    """Tests para casos extremos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            phone='1234567890'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_profile_image_without_file_field(self):
        """Test: Imagen de perfil sin campo de archivo"""
        # Crear registro sin imagen
        profile_image = UserProfileImage.objects.create(user=self.user)
        
        url = reverse('image_storage:user-profile-image')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_image'])
        self.assertIsNone(response.data['image_url'])
    
    def test_service_image_without_file_field(self):
        """Test: Imagen de servicio sin campo de archivo"""
        provider = Provider.objects.create(
            user=self.user
        )
        category = Category.objects.create(
            name='Test Category',
            description='Test Category Description'
        )
        
        service = Service.objects.create(
            provider=provider,
            title='Test Service',
            description='Test Description',
            category=category,
            price=100.00,
            duration_minutes=60
        )
        
        # Crear registro sin imagen
        service_image = ServiceImage.objects.create(
            service=service,
            is_primary=True
        )
        
        url = reverse('image_storage:service-images-list', kwargs={'service_id': service.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_images'])
        self.assertEqual(response.data['total_images'], 1)
        # La imagen debe aparecer pero sin URL
        self.assertIsNone(response.data['images'][0]['image_url'])
    
    def test_multiple_services_without_images(self):
        """Test: Múltiples servicios sin imágenes"""
        provider = Provider.objects.create(
            user=self.user
        )
        
        # Crear categoría
        category = Category.objects.create(
            name='Test Category',
            description='Test Category Description'
        )
        
        # Crear múltiples servicios sin imágenes
        services = []
        for i in range(3):
            service = Service.objects.create(
                provider=provider,
                title=f'Service {i}',
                description=f'Description {i}',
                category=category,
                price=100.00 + i,
                duration_minutes=60
            )
            services.append(service)
        
        # Verificar cada servicio
        for service in services:
            url = reverse('image_storage:service-images-list', kwargs={'service_id': service.id})
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(response.data['has_images'])
            self.assertEqual(response.data['total_images'], 0)
    
    def test_user_without_any_data(self):
        """Test: Usuario completamente nuevo sin datos"""
        new_user = User.objects.create_user(
            username='newuser',
            password='testpass123',
            phone='0987654321'
        )
        
        self.client.force_authenticate(user=new_user)
        
        # Verificar perfil sin imagen
        url = reverse('image_storage:user-profile-image')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_image'])
        
        # Verificar logs vacíos
        logs_url = reverse('image_storage:upload-logs')
        response = self.client.get(logs_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) 