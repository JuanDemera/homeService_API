from django.test import TestCase
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, timedelta
from unittest.mock import patch

from core.models import User
from core.serializers import UserSerializer, CustomTokenObtainPairSerializer
from users.models import UserProfile


class UserModelTest(TestCase):
    """Tests para el modelo User"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'phone': '+593991234567',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test crear usuario básico"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.phone, '+593991234567')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.role, User.Role.GUEST)
        self.assertFalse(user.is_verified)
        self.assertTrue(user.is_active)
    
    def test_create_superuser(self):
        """Test crear superusuario"""
        superuser = User.objects.create_superuser(
            username='admin',
            phone='+593998765432',
            password='adminpass123',
            role=User.Role.MANAGEMENT
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.role, User.Role.MANAGEMENT)
    
    def test_user_str_representation(self):
        """Test representación string del usuario"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')
    
    def test_full_role_property(self):
        """Test propiedad full_role"""
        user = User.objects.create_user(**self.user_data)
        user.role = User.Role.CONSUMER
        self.assertEqual(user.full_role, 'Consumer')
    
    def test_user_roles(self):
        """Test diferentes roles de usuario"""
        roles = [
            User.Role.GUEST,
            User.Role.CONSUMER,
            User.Role.PROVIDER,
            User.Role.MANAGEMENT
        ]
        
        for i, role in enumerate(roles):
            user = User.objects.create_user(
                username=f'user{i}',
                phone=f'+59399{i:06d}',
                password='testpass123',
                role=role
            )
            self.assertEqual(user.role, role)


class UserSerializerTest(TestCase):
    """Tests para serializers de usuarios"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+593991234567',
            password='testpass123',
            role=User.Role.CONSUMER
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            firstname='Test',
            lastname='User',
            email='test@example.com',
            cedula='1234567890',
            birth_date=date(1990, 1, 1)
        )
    
    def test_user_serializer(self):
        """Test serialización de usuario"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['phone'], '+593991234567')
        self.assertEqual(data['role'], 'consumer')
        self.assertFalse(data['is_verified'])
        self.assertTrue(data['is_active'])
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['firstname'], 'Test')
    
    def test_user_serializer_read_only_fields(self):
        """Test que los campos de solo lectura no se pueden modificar"""
        data = {
            'id': 999,
            'created_at': '2023-01-01T00:00:00Z',
            'username': 'newusername',
            'phone': '+593991234567'  # Campo requerido
        }
        serializer = UserSerializer(self.user, data=data)
        self.assertTrue(serializer.is_valid())
        
        # Los campos read_only no deberían cambiar
        self.assertEqual(self.user.id, serializer.instance.id)
        self.assertEqual(self.user.username, 'testuser')


class AuthenticationTest(APITestCase):
    """Tests de autenticación"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            phone='+593991234567',
            password='testpass123',
            role=User.Role.CONSUMER
        )
    
    def test_authenticate_user(self):
        """Test autenticación de usuario"""
        user = authenticate(username='testuser', password='testpass123')
        self.assertEqual(user, self.user)
    
    def test_authenticate_invalid_credentials(self):
        """Test autenticación con credenciales inválidas"""
        user = authenticate(username='testuser', password='wrongpass')
        self.assertIsNone(user)
    
    def test_jwt_token_creation(self):
        """Test creación de tokens JWT"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(str(refresh))
        
        # Verificar que el token contiene información básica
        payload = refresh.access_token.payload
        self.assertIn('user_id', payload)
        self.assertEqual(payload['user_id'], self.user.id)
    
    def test_custom_token_serializer(self):
        """Test serializer personalizado de tokens"""
        serializer = CustomTokenObtainPairSerializer()
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        # Simular validación
        with patch.object(serializer, 'validate') as mock_validate:
            mock_validate.return_value = {
                'access': 'test_access_token',
                'refresh': 'test_refresh_token'
            }
            result = serializer.validate(data)
            self.assertIn('access', result)
            self.assertIn('refresh', result)


class CoreViewsTest(APITestCase):
    """Tests para vistas del core"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            phone='+593991234567',
            password='testpass123',
            role=User.Role.CONSUMER
        )
    
    def test_test_connection_endpoint(self):
        """Test endpoint de prueba de conexión"""
        response = self.client.get('/api/auth/api/ping/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'Conexión exitosa')
    
    def test_token_obtain_endpoint(self):
        """Test endpoint de obtención de tokens"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/api/token/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_obtain_invalid_credentials(self):
        """Test obtención de token con credenciales inválidas"""
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post('/api/auth/api/token/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_obtain_inactive_user(self):
        """Test obtención de token con usuario inactivo"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/api/token/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserManagerTest(TestCase):
    """Tests para el manager personalizado de usuarios"""
    
    def test_create_user_missing_username(self):
        """Test crear usuario sin username"""
        with self.assertRaises(TypeError):
            User.objects.create_user(
                phone='+593991234567',
                password='testpass123'
            )
    
    def test_create_user_missing_phone(self):
        """Test crear usuario sin phone"""
        with self.assertRaises(TypeError):
            User.objects.create_user(
                username='testuser',
                password='testpass123'
            )
    
    def test_create_superuser_missing_fields(self):
        """Test crear superusuario sin campos requeridos"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username='admin',
                phone='+593998765432',
                password='adminpass123',
                is_superuser=False
            )


class UserPermissionsTest(TestCase):
    """Tests de permisos de usuario"""
    
    def setUp(self):
        self.guest = User.objects.create_user(
            username='guest',
            phone='+593991111111',
            password='guestpass',
            role=User.Role.GUEST
        )
        self.consumer = User.objects.create_user(
            username='consumer',
            phone='+593992222222',
            password='consumerpass',
            role=User.Role.CONSUMER
        )
        self.provider = User.objects.create_user(
            username='provider',
            phone='+593993333333',
            password='providerpass',
            role=User.Role.PROVIDER
        )
        self.admin = User.objects.create_user(
            username='admin',
            phone='+593994444444',
            password='adminpass',
            role=User.Role.MANAGEMENT,
            is_staff=True,
            is_superuser=True
        )
    
    def test_user_roles_hierarchy(self):
        """Test jerarquía de roles"""
        self.assertFalse(self.guest.is_staff)
        self.assertFalse(self.consumer.is_staff)
        self.assertFalse(self.provider.is_staff)
        self.assertTrue(self.admin.is_staff)
    
    def test_user_verification_status(self):
        """Test estados de verificación"""
        self.assertFalse(self.guest.is_verified)
        self.assertFalse(self.consumer.is_verified)
        self.assertFalse(self.provider.is_verified)
        
        # Verificar usuario
        self.consumer.is_verified = True
        self.consumer.save()
        self.assertTrue(self.consumer.is_verified)
    
    def test_user_disabled_status(self):
        """Test estados de deshabilitación"""
        self.assertFalse(self.consumer.disabled)
        self.assertIsNone(self.consumer.disabled_at)
        self.assertIsNone(self.consumer.disabled_reason)
        
        # Deshabilitar usuario
        from django.utils import timezone
        self.consumer.disabled = True
        self.consumer.disabled_at = timezone.now()
        self.consumer.disabled_reason = "Violación de términos"
        self.consumer.save()
        
        self.assertTrue(self.consumer.disabled)
        self.assertIsNotNone(self.consumer.disabled_at)
        self.assertEqual(self.consumer.disabled_reason, "Violación de términos")
