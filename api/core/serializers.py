from rest_framework import serializers, status
from rest_framework.response import Response
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.contrib.auth.models import User
from .models import Profile


class RegisterSerializer(serializers.ModelSerializer):
    repeat_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'repeat_password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        repeat_password = validated_data['repeat_password']

        if password != repeat_password:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})

        user = User(username=username, email=email)
        user.set_password(password)
        user.save()

        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Profile"""
    class Meta:
        model = Profile
        fields = ('id', 'path', 'avatar_url', 'wrapper_url')


class UserSerializer(serializers.ModelSerializer):
    """User"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class RequestPasswordResetEmailSerializer(serializers.ModelSerializer):
    """Восстановление пароля по Email."""
    class Meta:
        model = User
        fields = 'email'


class SetNewPasswordSerializer(serializers.ModelSerializer):
    """Создание нового пароля"""
    password = serializers.CharField(write_only=True)
    repeat_password = serializers.CharField(write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        model = User
        fields = ('password', 'repeat_password', 'token', 'uidb64')

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            repeat_password = attrs.get('repeat_password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            user_pk = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_pk)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise Exception("AuthenticationFailed", "The reset link is invalid", 401)

            if password != repeat_password:
                raise serializers.ValidationError({'password': 'Пароли не совпадают'})

            user.set_password(password)
            user.save()

        except Exception:
            raise Exception("AuthenticationFailed", "The reset link is invalid", 401)
        return super().validate(attrs)