import re


from ..models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from ..profile.models_profile import Profile


class LoginSerializer(serializers.ModelSerializer):
    """Сериализация. Login'a"""
    path = serializers.SerializerMethodField()
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('path', 'username', 'email', 'password', 'token')
        read_only_fields = ('token',)

    def get_path(self, user):
        """Вернет путь до пользователя"""
        return Profile.objects.get(user=user).path


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализация. Регистрация пользователя"""
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @staticmethod
    def password_is_valid(password):
        """Проверка пароля на валидность"""
        reg = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}'
        if re.fullmatch(reg, password):
            return True
        return False

    def create(self, validated_data):
        """Создание пользователя"""
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']

        len_username = len(username)
        if 1 > len_username or len_username > 32:
            raise serializers.ValidationError({'error': 'username должно быть не больше 32 символов и не меньше 3'})
        if len(User.objects.filter(email=email)) != 0:
            raise serializers.ValidationError({'error': 'Пользователь с таким email уже существует'})
        if not self.password_is_valid(password):
            raise serializers.ValidationError({'error': 'Некорректный пароль'})

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
        """Проверка на валидность токена"""
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
