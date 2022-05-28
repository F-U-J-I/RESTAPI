from django.contrib.auth.models import User
from rest_framework import serializers

from .models_profile import Profile, Subscription


class HelperSerializer(serializers.ModelSerializer):
    @staticmethod
    def is_subscribed(subscribing, subscriber):
        """
        subscribing: на кого подписались
        subscriber: кто подписался
        :return: True, если subscriber подписан на goal. False если нет
        """
        subscription_list = Subscription.objects.filter(subscribing=subscribing, subscriber=subscriber)
        if len(subscription_list):
            return True
        return False


class ProfileSerializer(serializers.ModelSerializer):
    """Profile"""
    username = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'avatar_url', 'path', 'description', 'is_subscribed')

    def get_username(self, profile):
        return profile.user.username

    def get_is_subscribed(self, profile):
        auth = self.context.get('auth')
        if auth != profile:
            return HelperSerializer.is_subscribed(subscribing=profile, subscriber=auth)
        return None


class MiniProfileSerializer(serializers.ModelSerializer):
    """Mini Profile"""
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'avatar_url', 'path')

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
            'subscribing_quantity': len(Subscription.objects.filter(subscriber=profile)),
            'subscribers_quantity': len(Subscription.objects.filter(subscribing=profile)),
        }

    def get_is_subscribed(self, profile):
        auth = self.context.get('auth')
        if auth != profile:
            return HelperSerializer.is_subscribed(subscribing=profile, subscriber=auth)
        return None


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
