from django.test import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta, time, date

from core.models import User
from users.models import UserProfile
from providers.models import Provider
from providers.services.models import Category, Service


class EndToEndReservationFlowTest(TestCase):
    """Test de integración end-to-end: crear cita + carrito + pago simulado.

    Cubre:
      - Creación de consumer y provider aprobado con servicio activo
      - Autenticación JWT del consumer
      - Crear cita temporal (appointment)
      - Agregar servicio al carrito
      - Simular pago (payments/simulate) con cart_id y appointment_id
      - Verificar que la cita queda pagada (pending, no temporal) y carrito vacío
    """

    def setUp(self):
        # Crear consumer
        self.consumer = User.objects.create_user(
            username="consumer_test",
            phone="+593000000001",
            password="secret",
            role=User.Role.CONSUMER,
        )
        UserProfile.objects.create(
            user=self.consumer,
            firstname="Cons",
            lastname="Umer",
            email="cons@example.com",
            birth_date=date(2000, 1, 1),
        )

        # Crear provider aprobado
        self.provider_user = User.objects.create_user(
            username="provider_test",
            phone="+593000000002",
            password="secret",
            role=User.Role.PROVIDER,
        )
        self.provider = Provider.objects.create(
            user=self.provider_user,
            bio="Proveedor demo",
            is_active=True,
            verification_status=Provider.VerificationStatus.APPROVED,
        )

        # Crear categoría y servicio activo
        self.category = Category.objects.create(name="Limpieza")
        self.service = Service.objects.create(
            provider=self.provider,
            title="Limpieza de Cocina",
            description="Servicio de limpieza",
            category=self.category,
            price=50.00,
            duration_minutes=60,
            is_active=True,
        )

        # Cliente API
        self.client = APIClient()

        # Autenticación JWT
        resp = self.client.post(
            "/api/auth/api/token/",
            {"username": self.consumer.username, "password": "secret"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_full_checkout_flow(self):
        # 1) Crear appointment temporal
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        resp = self.client.post(
            "/api/appointments/consumer/create/",
            {
                "service": self.service.id,
                "appointment_date": tomorrow.isoformat(),
                "appointment_time": "14:00",
                "notes": "Reserva de prueba",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        appointment_id = resp.data["id"]
        self.assertTrue(resp.data.get("is_temporary", False))

        # 2) Agregar al carrito
        resp = self.client.post(
            "/api/carts/add/",
            {"service_id": self.service.id, "quantity": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)

        # 3) Obtener carrito y cart_id
        resp = self.client.get("/api/carts/")
        self.assertEqual(resp.status_code, 200, resp.content)
        cart_id = resp.data["id"]
        self.assertGreaterEqual(len(resp.data.get("items", [])), 1)

        # 4) Simular pago
        resp = self.client.post(
            "/api/payments/simulate/",
            {
                "cart_id": cart_id,
                "payment_method": "credit_card",
                "currency": "USD",
                "appointment_id": appointment_id,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.data.get("status"), "simulation_success")

        # 5) Verificar estado de appointment (ya no temporal, pending y pagado)
        resp = self.client.get(f"/api/appointments/consumer/{appointment_id}/")
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertFalse(resp.data.get("is_temporary"))
        self.assertTrue(resp.data.get("payment_completed"))
        self.assertEqual(resp.data.get("status"), "pending")

        # 6) Verificar carrito vacío
        resp = self.client.get("/api/carts/")
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(len(resp.data.get("items", [])), 0)


# Create your tests here.
