from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Product, Category, Order, Feedback
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, CategorySerializer,
    OrderCreateSerializer, OrderListSerializer, OrderDetailSerializer,
    RegisterSerializer, ProfileSerializer, FeedbackSerializer
)


# 1. Список товаров (с фильтрами)
class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(in_stock=True)
        # Фильтр по категории (slug)
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        # Фильтр по популярности
        is_popular = self.request.query_params.get('is_popular')
        if is_popular == 'true':
            queryset = queryset.filter(is_popular=True)
        # Фильтр по новинкам
        is_new = self.request.query_params.get('is_new')
        if is_new == 'true':
            queryset = queryset.filter(is_new=True)
        return queryset


# 2. Детальная страница товара
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]


# 3. Список категорий
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


# 4. Создание заказа
class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()


# 5. Список заказов текущего пользователя (только авторизованные)
class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


# 6. Детали заказа (только авторизованные и только свой заказ)
class UserOrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# 7. Регистрация пользователя
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# 8. Профиль пользователя (получение и обновление)
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# 9. Обратная связь
class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()