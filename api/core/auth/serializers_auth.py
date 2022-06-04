from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.validators import validate_email
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserAuthSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not (email and password):
            raise ValidationError("Вы не указали email или password")
        if len(User.objects.filter(email=email)) == 0:
            raise ValidationError("Такого email не существует")

        user_request = User.objects.get(email=email)
        user = authenticate(username=user_request.username, password=password)

        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']

        len_username = len(username)
        if 3 > len_username or len_username > 32:
            raise serializers.ValidationError({'error': 'username должно быть не больше 32 символов и не меньше 3'})
        if len(User.objects.filter(email=email)) != 0:
            raise serializers.ValidationError({'error': 'Пользователь с таким email уже существует'})

        user = User(username=username, email=email)
        user.set_password(password)
        user.save()

        return user


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
