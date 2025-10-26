import re
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        if not phone:
            raise ValueError('O número de telefone é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, phone=phone, **extra_fields)
        user.set_password(password)
        user.full_clean()  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=9, unique=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_generated_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def clean(self):
        if not re.match(r'^(92|93|94|97)\d{7}$', self.phone):
            raise ValidationError({
                'phone': "Number must be Unitel (starts with 92, 93, 94 ou 97) and must have 9 digits total."
            })

    def save(self, *args, **kwargs):
        self.phone = str(self.phone).strip()
        if self.phone.startswith('+244'):
            self.phone = self.phone.replace('+244', '')
        elif self.phone.startswith('00244'):
            self.phone = self.phone.replace('00244', '')
        super().save(*args, **kwargs)
