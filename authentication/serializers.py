from django.db.models import fields
from .models import User
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
import uuid
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        exclude = []


class UserCreationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(default=uuid.uuid4)
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    phonenumber = PhoneNumberField(allow_null=False, allow_blank=False)
    password = serializers.CharField(min_length=6, write_only=True)

    class Meta(object):
        model = User
        exclude = []
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        username_exists = User.objects.filter(username=attrs['username']).exists()
        if username_exists:
            raise serializers.ValidationError("Username Already Exists")
        email_exists = User.objects.filter(email=attrs['email']).exists()
        if email_exists:
            raise serializers.ValidationError("Email Already Exists")
        phonenumber_exists = User.objects.filter(phonenumber=attrs['phonenumber']).exists()
        if phonenumber_exists:
            raise serializers.ValidationError("PhoneNumber Already Exists")
        return super().validate(attrs)


class UserChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    class Meta(object):
        model = User
        exclude = []

    def validate(self, attrs):
        old_password = attrs['old_password']
        new_password = attrs['new_password']
        confirm_new_password = attrs['confirm_new_password']
        if new_password != confirm_new_password:
            raise serializers.ValidationError("New Password and Confirm New Passwords Doesn't match")
        elif not self.context['request'].user.check_password(old_password):
            raise serializers.ValidationError("OLD Password Provided is WRONG")
        elif new_password == old_password:
            raise serializers.ValidationError("New Password and Old Password cannot be same")
        return super().validate(attrs)


class UserSetNewPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=64, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    class Meta:
        model = User
        fields = ['password', 'uidb64', 'token']
    def validate(self, attrs):
        try:
            password = attrs.get('password', None)
            uidb64 = attrs.get('uidb64', None)
            token = attrs.get('token', None)
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id = id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Authentication Failed")
            user.set_password(password)
            user.save()
            return super().validate(attrs)

        except Exception as ex:
            raise serializers.ValidationError("Some Error Occured during validation")


class UserLogoutSerializer(serializers.ModelSerializer):
    refresh = serializers.CharField()
    default_error_messages = {
        'bad_token': "Token is Expired on Invalid"
    }
    class Meta:
        model = User
        exclude = ['password', 'email', 'username', 'phonenumber']
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception as ex:
            self.fail('bad_token')