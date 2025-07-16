from django.urls import path
from .views import CategoryListView, ServiceListView, ServiceCreateView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/create/', ServiceCreateView.as_view(), name='service-create'),
]