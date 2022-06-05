from django.contrib.auth.models import User
from rest_framework import serializers

from .models_profile import Profile, Subscription
from ..utils import Util


class HelperSerializer(serializers.ModelSerializer):
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
    """Profile"""
    username = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('path', 'username', 'avatar_url', 'description', 'is_subscribed')

    def get_username(self, profile):
        return profile.user.username

    def get_is_subscribed(self, profile):
        auth = self.context.get('auth')
        if auth != profile:
            return HelperSerializer.is_subscribed(goal=profile, subscriber=auth)
        return None


class MiniProfileSerializer(serializers.ModelSerializer):
    """Mini Profile"""
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('path', 'username', 'avatar_url')

    def get_username(self, profile):
        return profile.user.username


class HeaderProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    communications = serializers.SerializerMethodField(default=None)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'avatar_url', 'wrapper_url', 'communications', 'is_subscribed')

    def get_username(self, profile):
        return profile.user.username

    def get_communications(self, profile):
        return {
            'goal_quantity': len(Subscription.objects.filter(subscriber=profile)),
            'subscribers_quantity': len(Subscription.objects.filter(goal=profile)),
        }

    def get_is_subscribed(self, profile):
        auth = self.context.get('auth', None)
        if (auth is not None) and (auth != profile):
            return HelperSerializer.is_subscribed(goal=profile, subscriber=auth)
        return None


class ActionProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('avatar_url', 'path')

    def update(self, instance, validated_data):
        new_path = validated_data.get('path', -1)
        if new_path != -1:
            instance.path = Util.get_new_path(new_path=new_path, old_path=instance.path, model=Profile)

        new_image = validated_data.get('avatar_url', -1)
        if new_image != -1:
            default_image = Util.DEFAULT_IMAGES.get('profile')
            update_image = Util.get_image(old=instance.avatar_url, new=new_image, default=default_image)
            instance.avatar_url = Util.get_update_image(old=instance.image_url, new=update_image)

        instance.save()
        return instance


class ActionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    """User"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class ProfileAsAuthor(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'avatar_url')

    def get_username(self, profile):
        return profile.user.username
