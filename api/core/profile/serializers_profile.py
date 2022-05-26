from django.contrib.auth.models import User
from rest_framework import serializers

from .models_profile import Profile


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


class ProfileAsAuthor(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'avatar_url')

    def get_username(self, profile):
        return profile.user.username
