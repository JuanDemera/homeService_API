from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Service
from .serializers import CategorySerializer, ServiceSerializer, ServiceCreateSerializer
from rest_framework.exceptions import PermissionDenied

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

class ServiceListView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'provider']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']

    def get_queryset(self):
        return Service.objects.filter(is_active=True)

class ServiceCreateView(generics.CreateAPIView):
    serializer_class = ServiceCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'provider'):
            raise PermissionDenied("Only providers can create services")
        serializer.save(provider=self.request.user.provider)