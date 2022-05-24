from rest_framework import serializers, status
from rest_framework.response import Response
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.contrib.auth.models import User
from .models import Profile, Collection, Course, ProfileCollection, CourseCollection


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


class ProfileAsAuthor(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'avatar_url')

    def get_username(self, profile):
        return profile.user.username


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


class CourseSerializer(serializers.ModelSerializer):
    """Мини курс"""
    author = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('title', 'description', 'author', 'avatar_url', 'duration_in_minutes', 'rating', 'members_amount')

    def get_author(self, collection):
        return collection.profile.user.username


class MiniCourseSerializer(serializers.ModelSerializer):
    """Мини курс"""
    author = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('title', 'description', 'author', 'avatar_url', 'duration_in_minutes', 'rating', 'members_amount')

    def get_author(self, collection):
        return collection.profile.user.username


class CollectionSerializer(serializers.ModelSerializer):
    """
    Item Collection.
    Есть на странице каталога.
    Содержит: Подборки; Курсы в этой подборке; Добавил ли себе пользователь эту подборку
    """
    author = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    is_added = serializers.BooleanField(default=False)

    class Meta:
        model = Collection
        fields = ('title', 'author', 'image_url', 'rating', 'courses', 'is_added')

    @staticmethod
    def get_author(collection):
        return ProfileAsAuthor(collection.profile).data

    @staticmethod
    def get_courses(collection):
        courses_to_collection = CourseCollection.objects.filter(collection=collection)
        courses = list()
        for item in courses_to_collection:
            if item.course.status.name == 'Опубликован':
                courses.append(MiniCourseSerializer(item.course).data)
        courses = sorted(courses, key=lambda x: x['rating'])[:5]
        return courses

    @staticmethod
    def get_is_added(collection, auth_profile):
        profile_to_collection = ProfileCollection.objects.filter(collection=collection, profile=auth_profile)
        if profile_to_collection:
            return True
        return False


class MiniCollectionSerializer(serializers.ModelSerializer):
    """
    Item Mini Collection.
    Подборка в малой форме с малым количеством информации.
    """
    author = serializers.SerializerMethodField()
    is_added = serializers.BooleanField(default=False)

    class Meta:
        model = Collection
        fields = ('title', 'author', 'image_url', 'is_added')

    @staticmethod
    def get_author(collection):
        return collection.profile.user.username

    @staticmethod
    def get_is_added(collection, auth_profile):
        profile_to_collection = ProfileCollection.objects.filter(collection=collection, profile=auth_profile)
        if profile_to_collection:
            return True
        return False


class DetailCollectionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    is_added = serializers.BooleanField(default=False)

    class Meta:
        model = Collection
        fields = ('title', 'author', 'description', 'wallpaper', 'image_url', 'members_amount', 'rating', 'courses',
                  'is_added')

    @staticmethod
    def get_author(collection):
        return ProfileAsAuthor(collection.profile).data

    @staticmethod
    def get_courses(collection):
        courses_to_collection = CourseCollection.objects.filter(collection=collection)
        courses = list()
        for item in courses_to_collection:
            if item.course.status.name == 'Опубликован':
                courses.append(MiniCourseSerializer(item.course).data)
        # courses = sorted(courses, key=lambda x: x['rating'])[:5]
        return courses

    @staticmethod
    def get_is_added(collection, auth_profile):
        profile_to_collection = ProfileCollection.objects.filter(collection=collection, profile=auth_profile)
        if profile_to_collection:
            return True
        return False


class EditDetailCollectionSerializer(serializers.ModelSerializer):
    # image_url = serializers.ImageField(_DjangoImageField=SVG)
    collection_pk = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Collection
        fields = ('title', 'description', 'wallpaper', 'image_url', 'path', 'collection_pk')

    # def update_path(self, path):
    #

    def validate(self, attrs):
        collection = Collection.objects.get(pk=attrs.get('collection_pk'))

        title = attrs.get('title')
        if title != 0 and title != collection.title:
            collection.title = title

        description = attrs.get('description', 0)
        if description != 0 and description != collection.description:
            collection.description = description

        wallpaper = attrs.get('wallpaper', 0)
        if wallpaper != 0 and wallpaper != collection.wallpaper:
            collection.wallpaper = wallpaper

        image_url = attrs.get('image_url', 0)
        if image_url != 0 and image_url != collection.image_url:
            collection.image_url = image_url

        image_url = attrs.get('image_url', 0)
        if image_url != 0 and image_url != collection.image_url:
            collection.image_url = image_url

        collection.save()

        return super().validate(attrs)
