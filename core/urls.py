# core/urls.py

from django.urls import path
from .views import ProductCreateAPIView, ProductRetrieveAPIView, ProductListAPIView

urlpatterns = [
    path('create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('<int:pk>/', ProductRetrieveAPIView.as_view(), name='product-retrieve'),
    path('', ProductListAPIView.as_view(), name='product-list'),
]
