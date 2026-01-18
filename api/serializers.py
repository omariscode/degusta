import re
import random
from rest_framework import serializers
from .utils.sms import send_sms
from rest_framework.exceptions import ValidationError
from .models import (
    invoice_model,
    marketing_model,
    order_model,
    product_model,
    user_model,
    motoboy_model,
    role_model,
    notification_model
)
from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

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
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


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
        user.role, created = role_model.Role.objects.get_or_create(name="ADMIN")
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
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = product_model.Product
        fields = ["id", "name", "price", "final_price", "image"]

    def get_final_price(self, product):
        campaign = self.context.get("campaign")

        if campaign and campaign.discount_percent:
            discount = (campaign.discount_percent / 100) * product.price
            return round(product.price - discount, 2)

        return product.price



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


class MarketingSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    start_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y", "%Y-%m-%d"], required=False)
    end_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y", "%Y-%m-%d"], required=False)

    class Meta:
        model = marketing_model.Marketing
        fields = [
            "id", "title", "cover",
            "discount_percent", "is_combo",
            "start_date", "end_date",
            "products"
        ]

    def get_products(self, obj):
        serializer = ProductSerializer(
            obj.products.all(),
            many=True,
            context={"campaign": obj}
        )
        return serializer.data


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = role_model.Role
        fields = ["id", "name"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = notification_model.Notification
        fields = [
            "id",
            "title",
            "content",
            "created_at",
        ]

class PasswordResetRequestSMSSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate_phone(self, value):
        try:
            user = User.objects.get(phone=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado com esse telefone.")
        return value

    def save(self):
        phone = self.validated_data["phone"]
        user = User.objects.get(phone=phone)

        token = str(random.randint(100000, 999999))

        user.password_reset_token = token
        user.save()

        send_sms(
            f"Seu código de redefinição de senha é: {token}",
            to=user.phone
        )
        return token

class PasswordResetConfirmSMSSerializer(serializers.Serializer):
    phone = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        phone = attrs.get("phone")
        token = attrs.get("token")

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário inválido.")

        if user.password_reset_token != token:
            raise serializers.ValidationError("Token inválido ou expirado.")

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]

        user.set_password(new_password)
        user.password_reset_token = None  
        user.save()
        return user
