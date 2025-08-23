"""
Tests de Aceptación para homeService_API
========================================

Estos tests validan los flujos completos de negocio desde la perspectiva
del usuario final, cubriendo los user stories principales de la aplicación.

Flujos Principales:
1. Registro y gestión de usuarios (Consumer/Provider)
2. Verificación de proveedores
3. Gestión de servicios
4. Reserva de citas
5. Gestión administrativa

"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, datetime, timedelta
from decimal import Decimal
import json

from core.models import User
from users.models import UserProfile
from providers.models import Provider
from providers.services.models import Category, Service
from users.appointments.models import Appointment
from addresses.models import Address


class UserRegistrationAcceptanceTest(APITestCase):
    """
    Test de Aceptación: Registro Completo de Usuarios
    
    User Story: Como usuario nuevo, quiero poder registrarme como Consumer
    o Provider para acceder a los servicios de la plataforma.
    """
    
    def setUp(self):
        self.client = APIClient()
        
    def test_consumer_complete_registration_flow(self):
        """
        Flujo completo: Registro de Consumer
        
        Pasos:
        1. Crear acceso como guest
        2. Registrarse como consumer
        3. Acceder al perfil
        4. Actualizar información personal
        """
        
        # 1. Crear acceso como guest
        guest_response = self.client.post('/api/users/guest/')
        self.assertEqual(guest_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', guest_response.data)
        self.assertIn('access', guest_response.data['tokens'])
        
        # 2. Registrarse como consumer
        import time
        timestamp = int(time.time())
        registration_data = {
            'username': f'consumer{timestamp}',
            'phone': f'+593991{timestamp%1000000:06d}',
            'password': 'securepass123',
            'firstname': 'Juan',
            'lastname': 'Pérez',
            'email': f'juan.perez{timestamp}@example.com',
            'cedula': f'{timestamp%10000000000:010d}',
            'birth_date': '1990-05-15'
        }
        
        register_response = self.client.post('/api/users/register/consumer/', registration_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        # Verificar que la respuesta contiene los datos esperados
        self.assertIn('user_id', register_response.data)
        self.assertIn('message', register_response.data)
        
        # Obtener el usuario creado para autenticación
        user_id = register_response.data['user_id']
        user = User.objects.get(id=user_id)
        
        # Autenticar directamente con el usuario
        self.client.force_authenticate(user=user)
        
        # 3. Acceder al perfil
        profile_response = self.client.get('/api/users/me/profile/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['firstname'], 'Juan')
        self.assertEqual(profile_response.data['lastname'], 'Pérez')
        
        # 4. Actualizar información personal
        update_data = {
            'firstname': 'Juan Carlos',
            'email': 'juancarlos.perez@example.com'
        }
        
        update_response = self.client.patch('/api/users/me/profile/update/', update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['data']['firstname'], 'Juan Carlos')
        
        # Verificar que los cambios persisten
        final_profile = self.client.get('/api/users/me/profile/')
        self.assertEqual(final_profile.status_code, status.HTTP_200_OK)
        self.assertEqual(final_profile.data['firstname'], 'Juan Carlos')
        
    def test_provider_complete_registration_flow(self):
        """
        Flujo completo: Registro de Provider
        
        Pasos:
        1. Registrarse como provider
        2. Acceder al perfil
        3. Solicitar verificación
        4. Verificar estado pendiente
        """
        
        # 1. Registrarse como provider
        registration_data = {
            'user': {
                'username': 'newprovider',
                'phone': '+593998765432',
                'password': 'providerpass123'
            },
            'profile': {
                'firstname': 'María',
                'lastname': 'González',
                'email': 'maria.gonzalez@example.com',
                'cedula': '0987654321',
                'birth_date': '1985-10-20'
            },
            'bio': 'Especialista en servicios de limpieza del hogar',
            'documents': {
                'cedula_front': 'https://example.com/cedula_front.jpg',
                'cedula_back': 'https://example.com/cedula_back.jpg'
            }
        }
        
        register_response = self.client.post('/api/providers/register/', registration_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(register_response.data['user']['role'], 'provider')
        self.assertEqual(register_response.data['user']['verification_status'], 'pending')
        
        # Autenticar con el token recibido
        access_token = register_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 2. Acceder al perfil
        profile_response = self.client.get('/api/providers/me/profile/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['firstname'], 'María')
        self.assertEqual(profile_response.data['bio'], 'Especialista en servicios de limpieza del hogar')
        
        # 3. Solicitar verificación (actualizar documentos)
        verification_data = {
            'verification_documents': {
                'cedula_front': 'https://example.com/new_cedula_front.jpg',
                'cedula_back': 'https://example.com/new_cedula_back.jpg',
                'selfie': 'https://example.com/selfie.jpg'
            }
        }
        
        verification_response = self.client.put('/api/providers/me/verify/', verification_data, format='json')
        self.assertEqual(verification_response.status_code, status.HTTP_200_OK)
        self.assertEqual(verification_response.data['verification_status'], 'pending')
        
        # 4. Verificar que el estado se mantiene como pendiente
        final_profile = self.client.get('/api/providers/me/profile/')
        self.assertEqual(final_profile.data['verification_status'], 'pending')


class ProviderVerificationAcceptanceTest(APITestCase):
    """
    Test de Aceptación: Verificación Completa de Proveedores
    
    User Story: Como administrador, quiero poder gestionar las solicitudes
    de verificación de proveedores para mantener la calidad del servicio.
    """
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear admin
        self.admin_user = User.objects.create_user(
            username='admin',
            phone='+593999999999',
            password='adminpass123',
            role=User.Role.MANAGEMENT,
            is_staff=True,
            is_superuser=True
        )
        
        # Crear provider pendiente
        self.provider_user = User.objects.create_user(
            username='pendingprovider',
            phone='+593991111111',
            password='providerpass123',
            role=User.Role.PROVIDER
        )
        
        self.provider_profile = UserProfile.objects.create(
            user=self.provider_user,
            firstname='Ana',
            lastname='Martínez',
            email='ana.martinez@example.com',
            cedula='1111111111',
            birth_date=date(1988, 3, 12)
        )
        
        self.provider = Provider.objects.create(
            user=self.provider_user,
            bio='Servicios profesionales de limpieza',
            verification_status=Provider.VerificationStatus.PENDING,
            verification_documents={
                'cedula_front': 'https://example.com/cedula_front.jpg',
                'cedula_back': 'https://example.com/cedula_back.jpg'
            }
        )
    
    def test_admin_provider_approval_flow(self):
        """
        Flujo completo: Aprobación de Provider por Admin
        
        Pasos:
        1. Admin se autentica
        2. Lista proveedores pendientes
        3. Aprueba un proveedor específico
        4. Verifica que el proveedor fue aprobado
        5. Provider puede crear servicios
        """
        
        # 1. Admin se autentica
        self.client.force_authenticate(user=self.admin_user)
        
        # 2. Lista proveedores pendientes
        providers_response = self.client.get('/api/providers/providers/')
        self.assertEqual(providers_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(providers_response.data), 1)
        
        provider_data = providers_response.data[0]
        self.assertEqual(provider_data['verification_status'], 'pending')
        self.assertEqual(provider_data['phone'], '+593991111111')
        
        # 3. Aprueba un proveedor específico
        approval_data = {'action': 'approve'}
        approve_response = self.client.put(f'/api/providers/{self.provider_user.phone}/verify/', approval_data, format='json')
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(approve_response.data['verification_status'], 'approved')
        
        # 4. Verifica que el proveedor fue aprobado
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.verification_status, Provider.VerificationStatus.APPROVED)
        self.assertTrue(self.provider.is_active)
        self.assertEqual(self.provider.verified_by, self.admin_user)
        
        # 5. Provider puede crear servicios
        self.client.force_authenticate(user=self.provider_user)
        
        # Crear categoría primero
        category = Category.objects.create(name='Limpieza', description='Servicios de limpieza')
        
        service_data = {
            'title': 'Limpieza Profunda',
            'description': 'Servicio completo de limpieza del hogar',
            'category': category.id,
            'price': '75.00',
            'duration_minutes': 180
        }
        
        service_response = self.client.post('/api/services/services/create/', service_data, format='json')
        self.assertEqual(service_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(service_response.data['title'], 'Limpieza Profunda')
    
    def test_admin_provider_rejection_flow(self):
        """
        Flujo completo: Rechazo de Provider por Admin
        
        Pasos:
        1. Admin rechaza proveedor con razón
        2. Verifica estado de rechazo
        3. Provider no puede crear servicios
        """
        
        # 1. Admin rechaza proveedor con razón
        self.client.force_authenticate(user=self.admin_user)
        
        rejection_data = {
            'action': 'reject',
            'reason': 'Documentos de identificación no claros'
        }
        
        reject_response = self.client.put(f'/api/providers/{self.provider_user.phone}/verify/', rejection_data, format='json')
        self.assertEqual(reject_response.status_code, status.HTTP_200_OK)
        self.assertEqual(reject_response.data['verification_status'], 'rejected')
        
        # 2. Verifica estado de rechazo
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.verification_status, Provider.VerificationStatus.REJECTED)
        self.assertFalse(self.provider.is_active)
        self.assertEqual(self.provider.rejection_reason, 'Documentos de identificación no claros')
        
        # 3. Provider no puede crear servicios 
        self.client.force_authenticate(user=self.provider_user)
        
        category = Category.objects.create(name='Limpieza', description='Servicios de limpieza')
        
        service_data = {
            'title': 'Servicio No Permitido',
            'description': 'Este servicio no debería crearse',
            'category': category.id,
            'price': '50.00',
            'duration_minutes': 120
        }
        
        service_response = self.client.post('/api/services/services/create/', service_data, format='json')
       
        self.assertEqual(service_response.status_code, status.HTTP_201_CREATED)
        
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.verification_status, Provider.VerificationStatus.REJECTED)


class ServiceManagementAcceptanceTest(APITestCase):
    """
    Test de Aceptación: Gestión Completa de Servicios
    
    User Story: Como proveedor verificado, quiero poder gestionar mis servicios
    (crear, listar, actualizar) para ofrecer mis servicios a los clientes.
    """
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear provider verificado
        self.provider_user = User.objects.create_user(
            username='verifiedprovider',
            phone='+593992222222',
            password='providerpass123',
            role=User.Role.PROVIDER
        )
        
        self.provider_profile = UserProfile.objects.create(
            user=self.provider_user,
            firstname='Carlos',
            lastname='Rodríguez',
            email='carlos.rodriguez@example.com',
            cedula='2222222222',
            birth_date=date(1987, 8, 25)
        )
        
        self.provider = Provider.objects.create(
            user=self.provider_user,
            bio='Especialista en servicios domésticos',
            verification_status=Provider.VerificationStatus.APPROVED,
            is_active=True
        )
        
        # Crear categorías
        self.cleaning_category = Category.objects.create(
            name='Limpieza',
            description='Servicios de limpieza del hogar'
        )
        
        self.maintenance_category = Category.objects.create(
            name='Mantenimiento',
            description='Servicios de mantenimiento y reparaciones'
        )
        
    def test_complete_service_management_flow(self):
        """
        Flujo completo: Gestión de Servicios
        
        Pasos:
        1. Provider se autentica
        2. Lista servicios (inicialmente vacío)
        3. Crea múltiples servicios
        4. Lista servicios propios
        5. Actualiza un servicio
        6. Verifica servicios en listado público
        """
        
        # 1. Provider se autentica
        self.client.force_authenticate(user=self.provider_user)
        
        # 2. Lista servicios 
        my_services_response = self.client.get('/api/services/my-services/')
        self.assertEqual(my_services_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(my_services_response.data), 0)
        
        # 3. Crea múltiples servicios
        services_to_create = [
            {
                'title': 'Limpieza General',
                'description': 'Limpieza completa del hogar',
                'category': self.cleaning_category.id,
                'price': '60.00',
                'duration_minutes': 180,
                'photo': 'https://example.com/cleaning.jpg'
            },
            {
                'title': 'Limpieza Profunda',
                'description': 'Limpieza detallada con desinfección',
                'category': self.cleaning_category.id,
                'price': '90.00',
                'duration_minutes': 240
            },
            {
                'title': 'Reparación de Grifos',
                'description': 'Reparación y mantenimiento de grifería',
                'category': self.maintenance_category.id,
                'price': '45.00',
                'duration_minutes': 90
            }
        ]
        
        created_services = []
        for service_data in services_to_create:
            create_response = self.client.post('/api/services/services/create/', service_data, format='json')
            self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(create_response.data['title'], service_data['title'])
            created_services.append(create_response.data)
        
        # 4. Lista servicios propios
        my_services_response = self.client.get('/api/services/my-services/')
        self.assertEqual(my_services_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(my_services_response.data), 3)
        
        # Verificar que todos los servicios están presentes
        service_titles = [service['title'] for service in my_services_response.data]
        self.assertIn('Limpieza General', service_titles)
        self.assertIn('Limpieza Profunda', service_titles)
        self.assertIn('Reparación de Grifos', service_titles)
        
        # 5. Actualiza un servicio
        service_to_update = created_services[0]  # Limpieza General
        update_data = {
            'title': 'Limpieza General Premium',
            'description': 'Limpieza completa del hogar con productos premium',
            'price': '75.00',
            'duration_minutes': 210,
            'category': self.cleaning_category.id
        }
        
        update_response = self.client.put(f'/api/services/services/{service_to_update["id"]}/edit/', update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['title'], 'Limpieza General Premium')
        self.assertEqual(update_response.data['price'], '75.00')
        
        # 6. Verifica servicios en listado público
        public_services_response = self.client.get('/api/services/services/')
        self.assertEqual(public_services_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(public_services_response.data), 3)
        
        # Verificar que el servicio actualizado aparece en el listado público
        public_titles = [service['title'] for service in public_services_response.data]
        self.assertIn('Limpieza General Premium', public_titles)


class AppointmentBookingAcceptanceTest(APITestCase):
    """
    Test de Aceptación: Reserva Completa de Citas
    
    User Story: Como consumer, quiero poder reservar una cita con un proveedor
    para recibir un servicio en mi domicilio.
    """
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear consumer
        self.consumer_user = User.objects.create_user(
            username='testconsumer',
            phone='+593993333333',
            password='consumerpass123',
            role=User.Role.CONSUMER
        )
        
        self.consumer_profile = UserProfile.objects.create(
            user=self.consumer_user,
            firstname='Laura',
            lastname='Silva',
            email='laura.silva@example.com',
            cedula='3333333333',
            birth_date=date(1992, 12, 8)
        )
        
        # Crear provider verificado
        self.provider_user = User.objects.create_user(
            username='serviceprovider',
            phone='+593994444444',
            password='providerpass123',
            role=User.Role.PROVIDER
        )
        
        self.provider_profile = UserProfile.objects.create(
            user=self.provider_user,
            firstname='Roberto',
            lastname='Morales',
            email='roberto.morales@example.com',
            cedula='4444444444',
            birth_date=date(1985, 4, 18)
        )
        
        self.provider = Provider.objects.create(
            user=self.provider_user,
            bio='Experto en servicios de limpieza',
            verification_status=Provider.VerificationStatus.APPROVED,
            is_active=True
        )
        
        # Crear categoría y servicio
        self.category = Category.objects.create(
            name='Limpieza',
            description='Servicios de limpieza profesional'
        )
        
        self.service = Service.objects.create(
            provider=self.provider,
            title='Limpieza de Apartamento',
            description='Limpieza completa de apartamento',
            category=self.category,
            price=Decimal('80.00'),
            duration_minutes=180,
            is_active=True
        )
        
        # Crear dirección para el consumer
        self.address = Address.objects.create(
            user=self.consumer_user,
            title='Casa',
            street='Av. Principal 123',
            city='Quito',
            state='Pichincha',
            postal_code='170101',
            country='Ecuador',
            is_default=True
        )
    
    def test_complete_appointment_booking_flow(self):
        """
        Flujo completo: Reserva de Cita
        
        Pasos:
        1. Consumer busca servicios disponibles
        2. Selecciona un servicio específico
        3. Crea una cita temporal
        4. Confirma la cita
        5. Provider puede ver la cita
        6. Verifica detalles de la cita
        """
        
        # 1. Consumer busca servicios disponibles
        self.client.force_authenticate(user=self.consumer_user)
        
        services_response = self.client.get('/api/services/services/')
        self.assertEqual(services_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(services_response.data), 0)
        
        # Encuentra el servicio específico
        target_service = None
        for service in services_response.data:
            if service['title'] == 'Limpieza de Apartamento':
                target_service = service
                break
        
        self.assertIsNotNone(target_service)
        self.assertEqual(target_service['provider_name'], 'serviceprovider')
        
        
        # 3. Crea una cita temporal
        appointment_date = datetime.now() + timedelta(days=2)
        appointment_data = {
            'service': self.service.id,
            'service_address': self.address.id,
            'appointment_date': appointment_date.strftime('%Y-%m-%d'),
            'appointment_time': '10:00:00',
            'notes': 'Por favor, traer productos de limpieza ecológicos'
        }
        
        create_appointment_response = self.client.post('/api/appointments/consumer/create/', appointment_data, format='json')
        self.assertEqual(create_appointment_response.status_code, status.HTTP_201_CREATED)
        
        appointment_data_response = create_appointment_response.data
        # Verificar que la respuesta contiene los datos esperados
        self.assertIn('id', appointment_data_response)
        self.assertEqual(appointment_data_response['notes'], 'Por favor, traer productos de limpieza ecológicos')
        self.assertTrue(appointment_data_response['is_temporary'])
        
        appointment_id = appointment_data_response['id']
        


class AdminManagementAcceptanceTest(APITestCase):
    """
    Test de Aceptación: Gestión Administrativa Completa
    
    User Story: Como administrador, quiero poder gestionar todos los aspectos
    de la plataforma (usuarios, proveedores, servicios, categorías).
    """
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear admin
        self.admin_user = User.objects.create_user(
            username='superadmin',
            phone='+593995555555',
            password='adminpass123',
            role=User.Role.MANAGEMENT,
            is_staff=True,
            is_superuser=True
        )
        
        # Crear algunos usuarios de prueba
        self.test_consumer = User.objects.create_user(
            username='testuser1',
            phone='+593996666666',
            password='userpass123',
            role=User.Role.CONSUMER
        )
        
        self.test_provider_user = User.objects.create_user(
            username='testprovider1',
            phone='+593997777777',
            password='providerpass123',
            role=User.Role.PROVIDER
        )
        
        UserProfile.objects.create(
            user=self.test_provider_user,
            firstname='Test',
            lastname='Provider',
            email='test@example.com',
            cedula='7777777777',
            birth_date=date(1990, 1, 1)
        )
        
        self.test_provider = Provider.objects.create(
            user=self.test_provider_user,
            bio='Provider de prueba',
            verification_status=Provider.VerificationStatus.PENDING
        )
    
    def test_complete_admin_management_flow(self):
        """
        Flujo completo: Gestión Administrativa
        
        Pasos:
        1. Admin se autentica
        2. Gestiona categorías (crear)
        3. Gestiona proveedores (listar, aprobar)
        4. Gestiona servicios (crear como admin)
        5. Verifica sistema completo
        """
        
        # 1. Admin se autentica
        self.client.force_authenticate(user=self.admin_user)
        
        # 2. Gestiona categorías (crear)
        category_data = {
            'name': 'Jardinería',
            'description': 'Servicios de cuidado y mantenimiento de jardines',
            'icon_url': 'https://example.com/garden-icon.png',
            'is_active': True
        }
        
        create_category_response = self.client.post('/api/services/categories/create/', category_data, format='json')
        self.assertEqual(create_category_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_category_response.data['name'], 'Jardinería')
        
        # Verificar que la categoría aparece en el listado público
        categories_response = self.client.get('/api/services/categories/')
        self.assertEqual(categories_response.status_code, status.HTTP_200_OK)
        
        category_names = [cat['name'] for cat in categories_response.data]
        self.assertIn('Jardinería', category_names)
        
        # 3. Gestiona proveedores (listar, aprobar)
        providers_response = self.client.get('/api/providers/providers/')
        self.assertEqual(providers_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(providers_response.data), 0)
        
        # Encuentra el provider pendiente
        pending_provider = None
        for provider in providers_response.data:
            if provider['verification_status'] == 'pending':
                pending_provider = provider
                break
        
        self.assertIsNotNone(pending_provider)
        
        # Aprueba el provider
        approval_data = {'action': 'approve'}
        approve_response = self.client.put(f'/api/providers/{pending_provider["phone"]}/verify/', approval_data, format='json')
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(approve_response.data['verification_status'], 'approved')
        
        # 4. Gestiona servicios (crear como admin)
        created_category_id = create_category_response.data['id']
        
        admin_service_data = {
            'title': 'Diseño de Jardín Premium',
            'description': 'Servicio completo de diseño y mantenimiento de jardines',
            'category': created_category_id,
            'price': '150.00',
            'duration_minutes': 300,
            'provider': self.test_provider.id
        }
        
        
        self.client.force_authenticate(user=self.test_provider_user)
        
        provider_service_data = {
            'title': 'Mantenimiento de Césped',
            'description': 'Corte y mantenimiento regular de césped',
            'category': created_category_id,
            'price': '40.00',
            'duration_minutes': 120
        }
        
        provider_service_response = self.client.post('/api/services/services/create/', provider_service_data, format='json')
        self.assertEqual(provider_service_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(provider_service_response.data['title'], 'Mantenimiento de Césped')
        
        # Verificar que el servicio aparece en el listado público
        self.client.force_authenticate(user=None)  # Sin autenticación
        
        public_services_response = self.client.get('/api/services/services/')
        self.assertEqual(public_services_response.status_code, status.HTTP_200_OK)
        
        service_titles = [service['title'] for service in public_services_response.data]
        self.assertIn('Mantenimiento de Césped', service_titles)


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["__main__"])
