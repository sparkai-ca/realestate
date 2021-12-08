from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as ugtl
from phonenumber_field.modelfields import PhoneNumberField
import uuid


class AuthUserManager(BaseUserManager):

    def create(self, email, password, **extra_fields):
        if not email:
            raise ValueError(ugtl("Email is Required"))
        email = self.normalize_email(email)
        new_user = self.model(email=email, **extra_fields)
        new_user.set_password(password)
        new_user.save()
        return new_user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(ugtl("SuperUser Should have to be is_staff as True"))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(ugtl("SuperUser Should have to be is_superuser as True"))
        if extra_fields.get('is_active') is not True:
            raise ValueError(ugtl("SuperUser Should have to be is_active as True"))
        superuser = self.create(email=email, password=password, **extra_fields)
        return superuser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False, )
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phonenumber = PhoneNumberField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = AuthUserManager()

    def __str__(self):
        return f"<User {self.email}>"

        

