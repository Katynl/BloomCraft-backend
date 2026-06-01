from rest_framework import serializers
from django.contrib.auth import get_user_model
import cloudinary.uploader
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Category, Product, Order, OrderItem, Feedback
from django.contrib.auth.password_validation import validate_password

User = get_user_model()  # твоя кастомная модель пользователя

# Сериализатор категории
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'description']


# Сериализатор товара (список)
class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'image_url', 'in_stock', 'category', 'is_new', 'is_popular', 'is_gifts']
        # image стало image_url

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'image', 'in_stock', 'category',
                  'is_new', 'is_popular', 'is_gifts', 'description', 'specifications']
        # image остаётся только для приёма файла, в базу не льётся

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image', None)
        if image_file:
            # загрузка в Cloudinary
            upload_result = cloudinary.uploader.upload(
                image_file,
                folder="my_diplom_products"
            )
            instance.image_url = upload_result.get('secure_url')
        return super().update(instance, validated_data)

# Сериализатор товара (детальный, с описанием)
class ProductDetailSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ['description', 'specifications']


# Сериализатор для позиции заказа (используется внутри OrderSerializer)
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_slug', 'quantity', 'price']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'name', 'phone', 'email', 'comment', 'payment_method',
            'pickup_location', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        user = request.user

        total = 0

        order = Order.objects.create(
            user=user,
            total=0,
            **validated_data
        )

        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            quantity = int(item['quantity'])

            total += product.price * quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        order.total = total
        order.save(update_fields=['total'])

        return order

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'status': instance.status,
            'total': instance.total,
        }


# Сериализатор для чтения заказа (список заказов пользователя)
class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'created_at', 'total', 'status', 'payment_method']


# Сериализатор для детального просмотра заказа
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'created_at', 'name', 'phone', 'email', 'comment',
            'payment_method', 'pickup_location',
            'total', 'status', 'items',
        ]


# Сериализатор для регистрации пользователя
# serializers.py

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        error_messages={
            "required": "Введите имя пользователя.",
            "blank": "Введите имя пользователя.",
        },
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "Введите email.",
            "blank": "Введите email.",
            "invalid": "Введите корректный email.",
        },
    )
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        error_messages={
            "required": "Введите пароль.",
            "blank": "Введите пароль.",
            "min_length": "Пароль должен содержать минимум 6 символов.",
        },
    )
    password2 = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "Повторите пароль.",
            "blank": "Повторите пароль.",
        },
    )
    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2", "phone"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({
                "password2": "Пароли не совпадают."
            })
        return data

    def create(self, validated_data):
        validated_data.pop("password2")

        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            phone=validated_data.get("phone", ""),
        )

class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "Введите email.",
            "blank": "Введите email.",
            "invalid": "Введите корректный email.",
        },
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            "required": "Введите пароль.",
            "blank": "Введите пароль.",
        },
    )

    def validate(self, attrs):
        email = attrs.get("email", "").strip()
        password = attrs.get("password", "")

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": "Пользователь с таким email не найден."
            })

        if not user.check_password(password):
            raise serializers.ValidationError({
                "password": "Неправильный email или пароль."
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "detail": "Аккаунт отключён."
            })

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

# Сериализатор для профиля пользователя (чтение и обновление)
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'image']


# Сериализатор для обратной связи
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'name', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

class SimplePasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "Введите email.",
            "blank": "Введите email.",
            "invalid": "Введите корректный email.",
        },
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        error_messages={
            "required": "Введите новый пароль.",
            "blank": "Введите новый пароль.",
            "min_length": "Пароль должен содержать минимум 6 символов.",
        },
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            "required": "Повторите пароль.",
            "blank": "Повторите пароль.",
        },
    )

    def validate_email(self, value):
        email = value.strip()

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Пользователь с таким email не найден."
            )

        self.user = user
        return email

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({
                "password2": "Пароли не совпадают."
            })

        validate_password(data["password"], user=self.user)

        return data

    def save(self):
        user = self.user
        user.set_password(self.validated_data["password"])
        user.save(update_fields=["password"])
        return user