import re
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import (
    invoice_model,
    order_model,
    product_model,
    user_model,
    motoboy_model,
    notification_model,
    role_model
)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = user_model.User
        fields = ["id", "email", "name", "phone", "role" ,"is_active", "password"]

    def validate_phone(self, value):
        number = re.sub(r"\D", "", value)

        if len(number) > 9:
            raise ValidationError("Phone number cannot exceed 9 digits.")

        if not re.match(r"^(92|93|94|97)\d{7}$", number):
            raise ValidationError(
                "Number must be Unitel (starts with 92, 93, 94 ou 97) and must have 9 digits total."
            )

        if not number.isdigit():
            raise ValidationError("Phone number must contain only digits.")

        return number

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = user_model.User.objects.create(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = user_model.User
        fields = ["id", "email", "name", "phone", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = user_model.User.objects.create(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
    
class SuperAdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = user_model.User
        fields = ["id", "email", "name", "phone", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = user_model.User.objects.create(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.role, created = role_model.Role.objects.get_or_create(name="SUPERADMIN")
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = product_model.Product
        fields = ["id", "name", "slug", "description", "price", "stock", "image"]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = invoice_model.Invoice
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    invoice = InvoiceSerializer(read_only=True)

    class Meta:
        model = order_model.Order
        fields = "__all__"

    def get_invoice(self, obj):
        if hasattr(obj, "invoice") and obj.invoice:
            return obj.invoice.pdf_url
        return None


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = order_model.OrderItem
        fields = ["id", "product", "qty", "price"]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)
    invoice = InvoiceSerializer(read_only=True)

    class Meta:
        model = order_model.Order
        fields = [
            "id",
            "customer",
            "status",
            "total",
            "delivery_address",
            "invoice",
            "created_at",
            "items",
        ]

    def get_invoice(self, obj):
        if hasattr(obj, "invoice") and obj.invoice:
            return obj.invoice.pdf_url
        return None


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = motoboy_model.Courier
        fields = ["id", "name", "phone_number", "license_plate"]

    def validate_phone_number(self, value):
        number = re.sub(r"\D", "", value)

        if len(number) > 9:
            raise ValidationError("Phone number cannot exceed 9 digits.")

        if not re.match(r"^(92|93|94|97)\d{7}$", number):
            raise ValidationError(
                "Number must be Unitel (starts with 92, 93, 94 ou 97) and must have 9 digits total."
            )

        if not number.isdigit():
            raise ValidationError("Phone number must contain only digits.")

        return number


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = notification_model.Notification
        fields = ["id", "message", "created_at"]

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = role_model.Role
        fields = ["id", "name"]