from rest_framework import serializers

from .models_collection import Collection, ProfileCollection, CollectionStars
from ..course.models_course import ProfileCourse
from ..course.serializers_course import MiniCourseSerializer
from ..profile.serializers_profile import ProfileAsAuthor
from django.db.models import Q


#####################################
#       ##  COLLECTION ##
#####################################
from ..utils import Util


class HelperCollectionSerializer:
    @staticmethod
    def get_is_added(collection, profile):
        profile_to_collection = ProfileCollection.objects.filter(collection=collection, profile=profile)
        if profile_to_collection:
            return True
        return False


class CollectionSerializer(serializers.ModelSerializer):
    """
    Collection.
    Есть на странице каталога.
    Содержит: Подборки; Курсы в этой подборке; Добавил ли себе пользователь эту подборку
    """
    author = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    is_added = serializers.SerializerMethodField(default=False)
    added_number = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ('title', 'author', 'image_url', 'rating', 'courses', 'is_added', 'added_number')

    @staticmethod
    def get_author(collection):
        return collection.profile.user.username
        # return ProfileAsAuthor(collection.profile).data

    def get_courses(self, collection):
        courses_to_collection = ProfileCourse.objects.filter(collection=collection)
        courses = list()
        for item in courses_to_collection:
            if item.course.status.name == Util.COURSE_STATUS_RELEASE_NAME:
                courses.append(MiniCourseSerializer(item.course, context={'profile': self.context.get('profile')}).data)
        courses = sorted(courses, key=lambda x: x['rating'])[:5]
        return courses

    def get_is_added(self, collection):
        return HelperCollectionSerializer.get_is_added(collection=collection, profile=self.context.get('profile'))

    def get_added_number(self, collection):
        queryset = ProfileCollection.objects.filter(collection=collection, )
        return len(queryset.filter(~Q(profile=self.context.get('profile'))))


class MiniCollectionSerializer(serializers.ModelSerializer):
    """
    Item Mini Collection.
    Подборка в малой форме с малым количеством информации.
    """
    author = serializers.SerializerMethodField()
    is_added = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Collection
        fields = ('title', 'author', 'image_url', 'is_added')

    @staticmethod
    def get_author(collection):
        return collection.profile.user.username

    def get_is_added(self, collection):
        return HelperCollectionSerializer.get_is_added(collection=collection, profile=self.context.get('profile'))


class DetailCollectionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    is_added = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Collection
        fields = ('title', 'author', 'description', 'wallpaper', 'image_url', 'members_amount', 'rating', 'courses',
                  'is_added')

    @staticmethod
    def get_author(collection):
        return ProfileAsAuthor(collection.profile).data

    def get_courses(self, collection):
        courses_to_collection = CourseCollection.objects.filter(collection=collection)
        courses = list()
        for item in courses_to_collection:
            if item.course.status.name == Util.COURSE_STATUS_RELEASE_NAME:
                courses.append(MiniCourseSerializer(item.course, context={'profile': self.context.get('profile')}).data)
        return courses

    def get_is_added(self, collection):
        return HelperCollectionSerializer.get_is_added(collection=collection, profile=self.context.get('profile'))


class WindowDetailCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('title', 'description', 'wallpaper', 'image_url', 'path')

    def create(self, validated_data):
        return Collection.objects.create(**validated_data, profile=self.context.get('profile'))

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.wallpaper = validated_data.get('wallpaper', instance.wallpaper)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        instance.path = validated_data.get('path', instance.path)
        instance.save()
        return instance


#####################################

# #########################################
#        ######## GRADE ########
# #########################################

class GradeCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileCollection
        fields = ('grade',)

    @staticmethod
    def add_collection_star(collection, grade):
        stars = CollectionStars.objects.get(collection=collection)
        if grade == 1:
            stars.one_stars_count += 1
        elif grade == 2:
            stars.two_stars_count += 1
        elif grade == 3:
            stars.three_stars_count += 1
        elif grade == 4:
            stars.four_stars_count += 1
        elif grade == 5:
            stars.five_stars_count += 1
        stars.save()

    @staticmethod
    def difference_collection_star(collection, grade):
        stars = CollectionStars.objects.get(collection=collection)
        if grade == 1:
            stars.one_stars_count -= 1
        elif grade == 2:
            stars.two_stars_count -= 1
        elif grade == 3:
            stars.three_stars_count -= 1
        elif grade == 4:
            stars.four_stars_count -= 1
        elif grade == 5:
            stars.five_stars_count -= 1
        stars.save()

    @staticmethod
    def update_rating_collection(collection):
        stars = CollectionStars.objects.get(collection=collection)

        sum_grade = stars.one_stars_count + stars.two_stars_count * 2 + stars.three_stars_count * 3 \
                    + stars.four_stars_count * 4 + stars.five_stars_count * 5
        count = stars.one_stars_count + stars.two_stars_count + stars.three_stars_count + stars.four_stars_count \
                + stars.five_stars_count
        print(sum_grade, count)
        rating = sum_grade / count
        collection.rating = rating
        collection.save()

    def create(self, validated_data):
        profile_collection = ProfileCollection.objects.get(profile=self.context.get('profile'),
                                                           collection=self.context.get('collection'))
        if profile_collection.grade is not None:
            raise serializers.ValidationError({'grade': 'Вы уже оценивали подборку'})

        profile_collection.grade = validated_data['grade']
        self.add_collection_star(collection=profile_collection.collection, grade=profile_collection.grade)
        self.update_rating_collection(collection=profile_collection.collection)
        profile_collection.save()
        return profile_collection

    def update(self, instance, validated_data):
        grade_list = (1, 2, 3, 4, 5)
        new_grade = validated_data.get('grade')
        if (type(new_grade) == int) and (new_grade in grade_list) and (instance.grade != new_grade):
            self.difference_collection_star(collection=instance.collection, grade=instance.grade)
            instance.grade = validated_data.get('grade')
            instance.save()
            self.add_collection_star(collection=instance.collection, grade=instance.grade)
            self.update_rating_collection(collection=instance.collection)
        return instance

    def delete_grade(self):
        profile_collection = self.context.get('profile_collection')
        if profile_collection.grade is not None:
            self.difference_collection_star(collection=profile_collection.collection, grade=profile_collection.grade)
            self.update_rating_collection(collection=profile_collection.collection)
            profile_collection.grade = None
            profile_collection.save()
        return profile_collection
