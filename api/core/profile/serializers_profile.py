from ..models import User
from rest_framework import serializers

from .models_profile import Profile, Subscription
from ..auth.serializers_auth import RegisterSerializer
from ..utils import Util


class HelperSerializer(serializers.ModelSerializer):
    """Serializer. Помощник сериализаций"""

    @staticmethod
    def is_subscribed(goal, subscriber):
        """
        goal: на кого подписались
        subscriber: кто подписался
        :return: True, если subscriber подписан на goal. False если нет
        """
        subscription_list = Subscription.objects.filter(goal=goal, subscriber=subscriber)
        if len(subscription_list):
            return True
        return False


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer. Профиль"""
    username = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('path', 'username', 'avatar_url', 'description', 'is_subscribed')

    def get_username(self, profile):
        """Вернет имя профиля"""
        return profile.user.username

    def get_is_subscribed(self, profile):
        """Вернет подписан ли пользователь на профиль"""
        auth = self.context.get('auth')
        if auth != profile:
            return HelperSerializer.is_subscribed(goal=profile, subscriber=auth)
        return None


class MiniProfileSerializer(serializers.ModelSerializer):
    """Serializer. Форма мини профиля"""
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('path', 'username', 'avatar_url')

    @staticmethod
    def get_username(profile):
        """Вернет имя пользователя"""
        return profile.user.username


class HeaderProfileSerializer(serializers.ModelSerializer):
    """Serializer. Шапка профиля"""
    username = serializers.SerializerMethodField()
    communications = serializers.SerializerMethodField(default=None)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'avatar_url', 'wrapper_url', 'communications', 'is_subscribed')

    @staticmethod
    def get_username(profile):
        """Вернет имя пользователя"""
        return profile.user.username

    @staticmethod
    def get_communications(profile):
        """Вернет количество подписчиков и подписок"""
        return {
            'goal_quantity': len(Subscription.objects.filter(subscriber=profile)),
            'subscribers_quantity': len(Subscription.objects.filter(goal=profile)),
        }

    def get_is_subscribed(self, profile):
        """Подписаны ли вы на этот профиль"""
        auth = self.context.get('auth', None)
        if (auth is not None) and (auth != profile):
            return HelperSerializer.is_subscribed(goal=profile, subscriber=auth)
        return None


class ActionProfileSerializer(serializers.ModelSerializer):
    """Serializer. Действия над профилем"""
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('avatar_url', 'username', 'email', 'path')

    @staticmethod
    def get_username(profile):
        return profile.user.username

    @staticmethod
    def get_email(profile):
        return profile.user.email

    def update(self, instance, validated_data):
        """Обновление данных"""
        new_path = validated_data.get('path', -1)
        if new_path != -1:
            instance.path = Util.get_new_path(new_path=new_path, old_path=instance.path, model=Profile)

        new_image = validated_data.get('avatar_url', -1)
        if new_image != -1:
            default_image = Util.DEFAULT_IMAGES.get('profile')
            update_image = Util.get_image(old=instance.avatar_url, new=new_image, default=default_image)
            instance.avatar_url = Util.get_update_image(old=instance.avatar_url, new=update_image)

        instance.save()
        return instance


class ActionUserSerializer(serializers.ModelSerializer):
    """Serializer. Действия над пользователем"""

    class Meta:
        model = User
        fields = ('username', 'email')

    def update(self, instance, validated_data):
        """Обновление"""
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


class ActionUserPasswordSerializer(serializers.ModelSerializer):
    """Serializer. Действия над паролем пользователя"""

    new_password = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('password', 'new_password')
        extra_kwargs = {
            'password': {'write_only': True},
            'new_password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        """Обновление"""
        password = validated_data.get('password')
        new_password = self.context.get('new_password')

        if instance.check_password(password):
            if not RegisterSerializer.password_is_valid(new_password):
                raise serializers.ValidationError({"error": "Новый пароль не корректен"})
            instance.set_password(new_password)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({"error": "Не правильный password"})


class UserSerializer(serializers.ModelSerializer):
    """Serializer. Пользователь"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class ProfileAsAuthor(serializers.ModelSerializer):
    """Serializer. Профиль как автор"""

    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('path', 'username', 'avatar_url')

    @staticmethod
    def get_username(profile):
        """Вернет имя пользователя"""
        return profile.user.username
