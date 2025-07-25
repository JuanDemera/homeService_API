from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Service
from .serializers import (
    CategorySerializer,
    ProviderServiceSerializer,
    ServiceCreateSerializer,
    ServiceUpdateSerializer,
    CategoryCreateSerializer
)
from rest_framework.exceptions import PermissionDenied


# 1. Lista de categorías (para todos)
class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.filter(is_active=True)
    pagination_class = None


# 2. Lista de servicios activos (para consumer)
class ServiceListView(generics.ListAPIView):
    serializer_class = ProviderServiceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Service.objects.filter(is_active=True)


# 3. Lista de servicios del provider autenticado
class ProviderMyServicesView(generics.ListAPIView):
    serializer_class = ProviderServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, 'provider'):
            raise PermissionDenied("Solo los proveedores pueden ver sus servicios")
        return Service.objects.filter(provider=self.request.user.provider)


# 4. Crear servicio (provider)
class ServiceCreateView(generics.CreateAPIView):
    serializer_class = ServiceCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'provider'):
            raise PermissionDenied("Solo los proveedores pueden crear servicios")
        serializer.save(provider=self.request.user.provider)


# 5. Editar un servicio del provider
class ServiceUpdateView(generics.UpdateAPIView):
    serializer_class = ServiceUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Service.objects.all()
    lookup_field = 'id'

    def get_object(self):
        service = super().get_object()
        if service.provider != self.request.user.provider:
            raise PermissionDenied("No puedes editar un servicio que no es tuyo")
        return service


# 6. Crear categoría (admin)
class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategoryCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.all()


# 7. Crear servicio como admin (opcional)
class AdminServiceCreateView(generics.CreateAPIView):
    serializer_class = ServiceCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Service.objects.all()
