from rest_framework import generics, permissions
from .models import FeePolicy
from .serializers import FeePolicySerializer
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

class FeePolicyListView(generics.ListCreateAPIView):
    serializer_class = FeePolicySerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']

    def get_queryset(self):
        return FeePolicy.objects.all().order_by('-valid_from')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class FeePolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeePolicy.objects.all()
    serializer_class = FeePolicySerializer
    permission_classes = [permissions.IsAdminUser]

class CurrentFeePolicyView(generics.ListAPIView):
    serializer_class = FeePolicySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        today = timezone.now().date()
        return FeePolicy.objects.filter(
            valid_from__lte=today,
            valid_to__gte=today,
            is_active=True
        )