from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Product, Category, Order, Feedback
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader


# 1. Список товаров (с фильтрами)
class ProductListView(generics.ListCreateAPIView):   # было ListAPIView
    queryset = Product.objects.filter(in_stock=True)  # если хочешь, чтобы созданные сразу были видны
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductListSerializer

    def perform_create(self, serializer):
        image_file = self.request.FILES.get('image')
        image_url = None
        if image_file:
            upload_result = cloudinary.uploader.upload(
                image_file,
                folder="my_diplom_products"
            )
            image_url = upload_result.get('secure_url')
        serializer.save(image_url=image_url)

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