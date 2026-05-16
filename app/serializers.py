from rest_framework import serializers
from django.contrib.auth import get_user_model
import cloudinary.uploader
from .models import Category, Product, Order, OrderItem, Feedback

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
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'phone']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Пароли не совпадают!')
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )
        return user


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