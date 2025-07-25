from django.urls import path
from .views import CategoryListView, ServiceListView, ServiceCreateView, CategoryCreateView, AdminServiceCreateView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/create/', ServiceCreateView.as_view(), name='service-create'),
]

urlpatterns += [
    path('services/admin-create/', AdminServiceCreateView.as_view(), name='admin-service-create'),
]