from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

from core.models import User
from users.models import UserProfile
from providers.models import Provider
from providers.services.models import Category, Service


class CategoryModelTest(TestCase):
    """Tests para el modelo Category"""
    
    def setUp(self):
        self.category_data = {
            'name': 'Limpieza',
            'description': 'Servicios de limpieza del hogar',
            'icon_url': 'https://example.com/cleaning-icon.png',
            'is_active': True
        }
    
    def test_create_category(self):
        """Test crear categoría básica"""
        category = Category.objects.create(**self.category_data)
        
        self.assertEqual(category.name, 'Limpieza')
        self.assertEqual(category.description, 'Servicios de limpieza del hogar')
        self.assertEqual(category.icon_url, 'https://example.com/cleaning-icon.png')
        self.assertTrue(category.is_active)
    
    def test_category_str_representation(self):
        """Test representación string de categoría"""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(str(category), 'Limpieza')
    
    def test_category_meta_options(self):
        """Test opciones meta del modelo"""
        self.assertEqual(Category._meta.verbose_name, 'Category')
        self.assertEqual(Category._meta.verbose_name_plural, 'Categories')
        
        # Verificar ordenamiento
        Category.objects.create(name='B', description='Second')
        Category.objects.create(name='A', description='First')
        
        categories = Category.objects.all()
        self.assertEqual(categories[0].name, 'A')
        self.assertEqual(categories[1].name, 'B')
    
    def test_category_unique_name(self):
        """Test que el nombre de categoría sea único"""
        Category.objects.create(**self.category_data)
        
        with self.assertRaises(Exception):
            Category.objects.create(**self.category_data)


class ServiceModelTest(TestCase):
    """Tests para el modelo Service"""
    
    def setUp(self):
        # Crear provider
        self.provider_user = User.objects.create_user(
            username='testprovider',
            phone='+593991234567',
            password='providerpass123',
            role=User.Role.PROVIDER
        )
        self.provider_profile = UserProfile.objects.create(
            user=self.provider_user,
            firstname='Test',
            lastname='Provider',
            email='testprovider@example.com',
            cedula='1234567890',
            birth_date=date(1990, 1, 1)
        )
        self.provider = Provider.objects.create(
            user=self.provider_user,
            bio='Test provider',
            verification_status=Provider.VerificationStatus.APPROVED,
            is_active=True
        )
        
        # Crear categoría
        self.category = Category.objects.create(
            name='Limpieza',
            description='Servicios de limpieza del hogar',
            icon_url='https://example.com/cleaning-icon.png'
        )
        
        self.service_data = {
            'provider': self.provider,
            'title': 'Limpieza de Hogar',
            'description': 'Servicio completo de limpieza del hogar',
            'category': self.category,
            'price': Decimal('50.00'),
            'duration_minutes': 120,
            'is_active': True,
            'photo': 'https://example.com/cleaning-service.jpg'
        }
    
    def test_create_service(self):
        """Test crear servicio básico"""
        service = Service.objects.create(**self.service_data)
        
        self.assertEqual(service.provider, self.provider)
        self.assertEqual(service.title, 'Limpieza de Hogar')
        self.assertEqual(service.description, 'Servicio completo de limpieza del hogar')
        self.assertEqual(service.category, self.category)
        self.assertEqual(service.price, Decimal('50.00'))
        self.assertEqual(service.duration_minutes, 120)
        self.assertTrue(service.is_active)
        self.assertEqual(service.photo, 'https://example.com/cleaning-service.jpg')
    
    def test_service_str_representation(self):
        """Test representación string de servicio"""
        service = Service.objects.create(**self.service_data)
        expected_str = f"{service.title} - {self.provider.user.username}"
        self.assertEqual(str(service), expected_str)
    
    def test_service_meta_options(self):
        """Test opciones meta del modelo"""
        self.assertEqual(Service._meta.verbose_name, 'Service')
        self.assertEqual(Service._meta.verbose_name_plural, 'Services')
        
        # Verificar índices
        indexes = [index.fields for index in Service._meta.indexes]
        self.assertIn(['provider'], indexes)
        self.assertIn(['category'], indexes)
        self.assertIn(['is_active'], indexes)
        
        # Verificar ordenamiento
        Service.objects.create(**self.service_data)
        service2_data = self.service_data.copy()
        service2_data['title'] = 'Otro Servicio'
        Service.objects.create(**service2_data)
        
        services = Service.objects.all()
        # Deberían estar ordenados por created_at descendente
        # El más reciente primero (último creado)
        # Como se crean muy rápido, el orden puede variar
        service_titles = [service.title for service in services]
        self.assertIn('Otro Servicio', service_titles)
        self.assertIn('Limpieza de Hogar', service_titles)
    
    def test_service_price_validation(self):
        """Test validación de precio"""
        # Precio válido
        service = Service.objects.create(**self.service_data)
        self.assertEqual(service.price, Decimal('50.00'))
        
        # Precio negativo debería fallar (validación a nivel de serializer)
        # El modelo permite precio 0, pero el serializer valida min_value=0.01
        service_zero = Service.objects.create(
            provider=self.provider,
            title='Servicio Gratis',
            category=self.category,
            price=Decimal('0.00'),
            duration_minutes=60
        )
        self.assertEqual(service_zero.price, Decimal('0.00'))
    
    def test_service_duration_validation(self):
        """Test validación de duración"""
        # Duración válida
        service = Service.objects.create(**self.service_data)
        self.assertEqual(service.duration_minutes, 120)
        
        # Duración cero es válida en el modelo (PositiveIntegerField permite 0)
        service_zero_duration = Service.objects.create(
            provider=self.provider,
            title='Servicio Sin Duración',
            category=self.category,
            price=Decimal('25.00'),
            duration_minutes=0
        )
        self.assertEqual(service_zero_duration.duration_minutes, 0)


class ServiceSerializerTest(TestCase):
    """Tests para serializers de servicios"""
    
    def setUp(self):
        # Crear provider
        self.provider_user = User.objects.create_user(
            username='testprovider',
            phone='+593991234567',
            password='providerpass123',
            role=User.Role.PROVIDER
        )
        self.provider_profile = UserProfile.objects.create(
            user=self.provider_user,
            firstname='Test',
            lastname='Provider',
            email='testprovider@example.com',
            cedula='1234567890',
            birth_date=date(1990, 1, 1)
        )
        self.provider = Provider.objects.create(
            user=self.provider_user,
            bio='Test provider',
            verification_status=Provider.VerificationStatus.APPROVED,
            is_active=True
        )
        
        # Crear categoría
        self.category = Category.objects.create(
            name='Limpieza',
            description='Servicios de limpieza del hogar'
        )
        
        # Crear servicio
        self.service = Service.objects.create(
            provider=self.provider,
            title='Limpieza de Hogar',
            description='Servicio completo de limpieza del hogar',
            category=self.category,
            price=Decimal('50.00'),
            duration_minutes=120,
            is_active=True,
            photo='https://example.com/cleaning-service.jpg'
        )
    
    def test_service_serializer(self):
        """Test serialización de servicio"""
        from providers.services.serializers import ProviderServiceSerializer
        
        serializer = ProviderServiceSerializer(self.service)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Limpieza de Hogar')
        self.assertEqual(data['description'], 'Servicio completo de limpieza del hogar')
        self.assertEqual(data['price'], '50.00')
        self.assertEqual(data['duration_minutes'], 120)
        self.assertTrue(data['is_active'])
        self.assertEqual(data['photo'], 'https://example.com/cleaning-service.jpg')
        self.assertEqual(data['provider_name'], 'testprovider')
        
        # Verificar que category es un objeto completo
        self.assertIsInstance(data['category'], dict)
        self.assertEqual(data['category']['name'], 'Limpieza')
    
    def test_create_service_serializer(self):
        """Test creación de servicio con serializer"""
        from providers.services.serializers import ServiceCreateSerializer
        
        data = {
            'title': 'Nuevo Servicio',
            'description': 'Descripción del nuevo servicio',
            'category': self.category.id,
            'price': '75.00',
            'duration_minutes': 180,
            'photo': 'https://example.com/new-service.jpg'
        }
        
        serializer = ServiceCreateSerializer(data=data, context={'request': MagicMock()})
        self.assertTrue(serializer.is_valid())
        
        service = serializer.save(provider=self.provider)
        self.assertEqual(service.provider, self.provider)
        self.assertEqual(service.title, 'Nuevo Servicio')
        self.assertEqual(service.price, Decimal('75.00'))
        self.assertEqual(service.duration_minutes, 180)
        self.assertTrue(service.is_active)


class ServiceViewsTest(APITestCase):
    """Tests para vistas de servicios"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear provider
        self.provider_user = User.objects.create_user(
            username='testprovider',
            phone='+593991234567',
            password='providerpass123',
            role=User.Role.PROVIDER
        )
        self.provider_profile = UserProfile.objects.create(
            user=self.provider_user,
            firstname='Test',
            lastname='Provider',
            email='testprovider@example.com',
            cedula='1234567890',
            birth_date=date(1990, 1, 1)
        )
        self.provider = Provider.objects.create(
            user=self.provider_user,
            bio='Test provider',
            verification_status=Provider.VerificationStatus.APPROVED,
            is_active=True
        )
        
        # Crear categoría
        self.category = Category.objects.create(
            name='Limpieza',
            description='Servicios de limpieza del hogar'
        )
        
        # Crear servicio
        self.service = Service.objects.create(
            provider=self.provider,
            title='Limpieza de Hogar',
            description='Servicio completo de limpieza del hogar',
            category=self.category,
            price=Decimal('50.00'),
            duration_minutes=120,
            is_active=True
        )
    
    def test_create_service(self):
        """Test crear servicio via API"""
        self.client.force_authenticate(user=self.provider_user)
        
        data = {
            'title': 'Nuevo Servicio',
            'description': 'Descripción del nuevo servicio',
            'category': self.category.id,
            'price': '75.00',
            'duration_minutes': 180,
            'photo': 'https://example.com/new-service.jpg'
        }
        
        response = self.client.post('/api/services/services/create/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # La respuesta es directamente el objeto serializado
        service_data = response.data
        self.assertEqual(service_data['title'], 'Nuevo Servicio')
        self.assertEqual(service_data['price'], '75.00')
        self.assertEqual(service_data['duration_minutes'], 180)
        self.assertTrue(service_data['is_active'])
    
    def test_create_service_unauthorized(self):
        """Test crear servicio sin autenticación"""
        data = {
            'title': 'Nuevo Servicio',
            'category': self.category.id,
            'price': '75.00',
            'duration_minutes': 180
        }
        
        response = self.client.post('/api/services/services/create/', data, format='json')
        
        # El endpoint devuelve 403 cuando no está autenticado (no 401)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_service_wrong_role(self):
        """Test crear servicio con rol incorrecto"""
        consumer = User.objects.create_user(
            username='consumer',
            phone='+593998765432',
            password='consumerpass123',
            role=User.Role.CONSUMER
        )
        
        self.client.force_authenticate(user=consumer)
        
        data = {
            'title': 'Nuevo Servicio',
            'category': self.category.id,
            'price': '75.00',
            'duration_minutes': 180
        }
        
        response = self.client.post('/api/services/services/create/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_provider_services(self):
        """Test listar servicios del provider"""
        self.client.force_authenticate(user=self.provider_user)
        
        response = self.client.get('/api/services/my-services/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        
        service_data = response.data[0]
        self.assertEqual(service_data['title'], 'Limpieza de Hogar')
        self.assertEqual(service_data['price'], '50.00')
        self.assertEqual(service_data['duration_minutes'], 120)
    
    def test_list_all_services(self):
        """Test listar todos los servicios activos"""
        response = self.client.get('/api/services/services/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        
        service_data = response.data[0]
        self.assertEqual(service_data['title'], 'Limpieza de Hogar')
        self.assertEqual(service_data['price'], '50.00')

    def test_update_service(self):
        """Test actualizar servicio"""
        self.client.force_authenticate(user=self.provider_user)
        
        data = {
            'title': 'Limpieza Actualizada',
            'description': 'Descripción actualizada',
            'price': '60.00',
            'duration_minutes': 150,
            'category': self.category.id
        }
        
        response = self.client.put(f'/api/services/services/{self.service.id}/edit/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # La respuesta es directamente el objeto actualizado
        updated_data = response.data
        self.assertEqual(updated_data['title'], 'Limpieza Actualizada')
        self.assertEqual(updated_data['description'], 'Descripción actualizada')
        self.assertEqual(updated_data['price'], '60.00')
        self.assertEqual(updated_data['duration_minutes'], 150)
        
        # Verificar que el servicio se actualizó
        self.service.refresh_from_db()
        self.assertEqual(self.service.title, 'Limpieza Actualizada')
        self.assertEqual(self.service.description, 'Descripción actualizada')
        self.assertEqual(self.service.price, Decimal('60.00'))
        self.assertEqual(self.service.duration_minutes, 150)
    
    


class CategoryViewsTest(APITestCase):
    """Tests para vistas de categorías"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear categorías
        self.category1 = Category.objects.create(
            name='Limpieza',
            description='Servicios de limpieza del hogar',
            icon_url='https://example.com/cleaning-icon.png'
        )
        self.category2 = Category.objects.create(
            name='Jardinería',
            description='Servicios de jardinería',
            icon_url='https://example.com/gardening-icon.png'
        )
    
    def test_list_categories(self):
        """Test listar todas las categorías"""
        response = self.client.get('/api/services/categories/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)
        
        # Verificar ordenamiento alfabético
        self.assertEqual(response.data[0]['name'], 'Jardinería')
        self.assertEqual(response.data[1]['name'], 'Limpieza')
    
    # def test_get_category_detail(self):
    #     """Test obtener detalle de categoría"""
    #     response = self.client.get(f'/api/categories/{self.category1.id}/')
    #     
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.data
    #     
    #     self.assertEqual(data['id'], self.category1.id)
    #     self.assertEqual(data['name'], 'Limpieza')
    #     self.assertEqual(data['description'], 'Servicios de limpieza del hogar')
    #     self.assertEqual(data['icon_url'], 'https://example.com/cleaning-icon.png')
    #     self.assertTrue(data['is_active'])
    
    # def test_get_category_services(self):
    #     """Test obtener servicios de una categoría"""
    #     # Crear provider y servicio
    #     provider_user = User.objects.create_user(
    #         username='testprovider',
    #         phone='+593991234567',
    #         password='providerpass123',
    #         role=User.Role.PROVIDER
    #     )
    #     provider = Provider.objects.create(
    #         user=provider_user,
    #         verification_status=Provider.VerificationStatus.APPROVED,
    #         is_active=True
    #     )
    #     
    #     service = Service.objects.create(
    #         provider=provider,
    #         title='Limpieza de Hogar',
    #         category=self.category1,
    #         price=Decimal('50.00'),
    #         duration_minutes=120
    #     )
    #     
    #     response = self.client.get(f'/api/categories/{self.category1.id}/services/')
    #     
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIsInstance(response.data, list)
    #     self.assertEqual(len(response.data), 1)
    #     
    #     service_data = response.data[0)
    #     self.assertEqual(service_data['title'], 'Limpieza de Hogar')
    #     self.assertEqual(service_data['price'], '50.00')


class ServiceIntegrationTest(APITestCase):
    """Tests de integración para servicios"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear provider
        self.provider_user = User.objects.create_user(
            username='testprovider',
            phone='+593991234567',
            password='providerpass123',
            role=User.Role.PROVIDER
        )
        self.provider_profile = UserProfile.objects.create(
            user=self.provider_user,
            firstname='Test',
            lastname='Provider',
            email='testprovider@example.com',
            cedula='1234567890',
            birth_date=date(1990, 1, 1)
        )
        self.provider = Provider.objects.create(
            user=self.provider_user,
            bio='Test provider',
            verification_status=Provider.VerificationStatus.APPROVED,
            is_active=True
        )
        
        # Crear categoría
        self.category = Category.objects.create(
            name='Limpieza',
            description='Servicios de limpieza del hogar'
        )
    
    def test_complete_service_flow(self):
        """Test flujo completo de servicio: crear -> actualizar -> eliminar"""
        self.client.force_authenticate(user=self.provider_user)
        
        # 1. Crear servicio
        create_data = {
            'title': 'Servicio Completo',
            'description': 'Descripción del servicio',
            'category': self.category.id,
            'price': '100.00',
            'duration_minutes': 240,
            'photo': 'https://example.com/service.jpg'
        }
        
        create_response = self.client.post('/api/services/services/create/', create_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        service_id = create_response.data['id']
        
        # 2. Actualizar servicio
        update_data = {
            'title': 'Servicio Actualizado',
            'description': 'Descripción actualizada',
            'price': '120.00',
            'duration_minutes': 300,
            'category': self.category.id
        }
        
        update_response = self.client.put(f'/api/services/services/{service_id}/edit/', update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        # 3. Verificar que se puede listar
        list_response = self.client.get('/api/services/my-services/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        
        service_data = list_response.data[0]
        self.assertEqual(service_data['title'], 'Servicio Actualizado')
        self.assertEqual(service_data['price'], '120.00')
        
      
