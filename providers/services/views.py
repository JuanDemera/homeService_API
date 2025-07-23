from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Service
from .serializers import CategorySerializer, ProviderServiceSerializer, ServiceCreateSerializer, CategoryCreateSerializer
from rest_framework.exceptions import PermissionDenied

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    queryset = Category.objects.filter(is_active=True)

class ServiceListView(generics.ListAPIView):
    serializer_class = ProviderServiceSerializer 
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'provider', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Service.objects.filter(is_active=True)

class ServiceCreateView(generics.CreateAPIView):
    serializer_class = ServiceCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'provider'):
            raise PermissionDenied(
                detail="Only registered providers can create services",
                code="not_provider"
            )
        serializer.save(provider=self.request.user.provider)

class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategoryCreateSerializer
    permission_classes = [permissions.IsAdminUser]  # Solo admin puede crear
    queryset = Category.objects.all()