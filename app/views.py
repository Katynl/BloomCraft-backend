from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Product, Category, Order, Feedback
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader
from .permissions import IsAdminUserCustom
from rest_framework_simplejwt.views import TokenObtainPairView


# 1. Список товаров (с фильтрами)
class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(in_stock=True)

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

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
    permission_classes = [IsAuthenticated]

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

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class SimplePasswordResetView(generics.GenericAPIView):
    serializer_class = SimplePasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Пароль успешно изменён. Теперь можно войти с новым паролем."},
            status=status.HTTP_200_OK,
        )
    
class AdminOrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAdminUserCustom]

class AdminOrderDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAdminUserCustom]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AdminOrderStatusSerializer
        return OrderDetailSerializer

class AdminProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAdminUserCustom]

class AdminProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAdminUserCustom]

    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save()

class AdminProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAdminUserCustom]

    parser_classes = [MultiPartParser, FormParser]

class AdminProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAdminUserCustom]

class AdminFeedbackListView(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAdminUserCustom]