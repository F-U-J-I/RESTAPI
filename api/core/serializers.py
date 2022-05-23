from django.contrib.auth.models import User
from rest_framework import serializers

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
    class Meta:
        model = Profile
        fields = ('id', 'path', 'avatar_url', 'wrapper_url')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email')
