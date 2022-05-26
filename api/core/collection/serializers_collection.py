from rest_framework import serializers

from .models_collection import Collection, ProfileCollection, CourseCollection, CollectionStars
from ..course.serializers_course import MiniCourseSerializer
from ..profile.serializers_profile import ProfileAsAuthor


#####################################
#       ##  COLLECTION ##
#####################################


class HelperCollectionSerializer:
    @staticmethod
    def get_is_added(collection, profile):
        profile_to_collection = ProfileCollection.objects.filter(collection=collection, profile=profile)
        if profile_to_collection:
            return True
        return False


class CollectionSerializer(serializers.ModelSerializer):
    """
    Item Collection.
    Есть на странице каталога.
    Содержит: Подборки; Курсы в этой подборке; Добавил ли себе пользователь эту подборку
    """
    author = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    is_added = serializers.SerializerMethodField(default=False)

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

    def get_is_added(self, collection):
        return HelperCollectionSerializer.get_is_added(collection=collection, profile=self.context.get('profile'))


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

    @staticmethod
    def get_courses(collection):
        courses_to_collection = CourseCollection.objects.filter(collection=collection)
        courses = list()
        for item in courses_to_collection:
            if item.course.status.name == 'Опубликован':
                courses.append(MiniCourseSerializer(item.course).data)
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
    def update_collection_star(collection, grade):
        print('update_collection_star')
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
    def update_rating_collection(collection):
        print('update_rating_collection')
        stars = CollectionStars.objects.get(collection=collection)

        sum_grade = stars.one_stars_count + stars.two_stars_count * 2 + stars.three_stars_count * 3 \
                    + stars.four_stars_count * 4 + stars.five_stars_count * 5
        count = stars.one_stars_count + stars.two_stars_count + stars.three_stars_count + stars.four_stars_count \
                + stars.five_stars_count
        rating = sum_grade / count
        collection.rating = rating
        collection.save()

    def create(self, validated_data):
        print('create')
        profile_collection = ProfileCollection.objects.get(profile=self.context.get('profile'),
                                                           collection=self.context.get('collection'))
        profile_collection.grade = validated_data['grade']
        self.update_collection_star(collection=profile_collection.collection, grade=profile_collection.grade)
        self.update_rating_collection(collection=profile_collection.collection)
        return profile_collection

    def validate(self, attrs):
        print('validate')
        profile_collection = ProfileCollection.objects.get(profile=self.context.get('profile'),
                                                                collection=self.context.get('collection'))
        print(profile_collection)
        if profile_collection.grade is not None:
            raise BaseException('This user has already rated')
        return super().validate(attrs)

    # def update(self, instance, validated_data):
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.description = validated_data.get('description', instance.description)
    #     instance.wallpaper = validated_data.get('wallpaper', instance.wallpaper)
    #     instance.image_url = validated_data.get('image_url', instance.image_url)
    #     instance.path = validated_data.get('path', instance.path)
    #     instance.save()
    #     return instance
