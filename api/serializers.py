from rest_framework import serializers
from .models import invoice_model, order_model, product_model, user_model


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = user_model.User
        fields = ['id', 'email', 'name', 'phone', 'is_active', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = user_model.User.objects.create(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user



class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = user_model.User
        fields = ['id', 'email', 'name', 'phone', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = user_model.User.objects.create(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = product_model.Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'stock', 'image']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = invoice_model.Invoice
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = order_model.Order
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = order_model.OrderItem
        fields = ['id', 'product', 'qty', 'price']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)

    class Meta:
        model = order_model.Order
        fields = ['id', 'customer', 'status', 'total', 'delivery_address', 'created_at', 'items']