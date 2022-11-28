from django.db.models import Q
from rest_framework import serializers

from .models_collection import Collection, ProfileCollection, CollectionStars
from ..course.models_course import ProfileCourseCollection
from ..course.serializers_course import MiniCourseSerializer
from ..profile.serializers_profile import ProfileAsAuthor
#####################################
#       ##  COLLECTION ##
#####################################
from ..utils import Util


class HelperCollectionSerializer:
    """SERIALIZER. Помощник при сериализации"""

    @staticmethod
    def get_is_added(collection, profile):
        queryset = ProfileCollection.objects.filter(collection=collection, profile=profile)
        # print('-----')
        # print('get_is_added')
        # print(collection.title, queryset)

        for item in queryset:
            # print(collection.title, item.date_added)
            if item.date_added:
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
    count_ratings = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ('path', 'title', 'author', 'image_url', 'rating', 'courses', 'is_added', 'added_number',
                  'count_ratings')

    @staticmethod
    def get_author(collection):
        """Вернет автора подборки"""
        return ProfileAsAuthor(collection.profile).data

    def get_courses(self, collection):
        """Вернет первые 5 курсов которые есть в подборке"""
        courses_to_collection = ProfileCourseCollection.objects.filter(collection=collection)
        courses = list()
        for item in courses_to_collection:
            if item.course.status.name == Util.COURSE_STATUS_RELEASE_NAME:
                courses.append(MiniCourseSerializer(item.course, context={'profile': self.context.get('profile')}).data)
        courses = sorted(courses, key=lambda x: x['rating'])[:5]
        return courses

    def get_is_added(self, collection):
        """Добавлена ли эта подборка"""
        return HelperCollectionSerializer.get_is_added(collection=collection, profile=self.context.get('profile'))

    def get_added_number(self, collection):
        """Сколько людей добавило эту подборку"""
        queryset = ProfileCollection.objects.filter(collection=collection, )
        return len(queryset.filter(~Q(profile=self.context.get('profile'))))

    @staticmethod
    def get_count_ratings(collection):
        """Количество оценок подборки"""
        return GradeCollectionSerializer.get_count_star(collection=collection)


class MiniCollectionSerializer(serializers.ModelSerializer):
    """
    Item Mini Collection.
    Подборка в малой форме с малым количеством информации.
    """
    author = serializers.SerializerMethodField()
    is_added = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Collection
        fields = ('path', 'title', 'author', 'image_url', 'is_added', 'rating')

    @staticmethod
    def get_author(collection):
        """Вернет автора подборки"""
        return ProfileAsAuthor(collection.profile).data

    def get_is_added(self, collection):
        """Добавлена ли подборка"""
        return HelperCollectionSerializer.get_is_added(collection=collection, profile=self.context.get('profile'))


class DetailCollectionSerializer(serializers.ModelSerializer):
    """SERIALIZER. Дательная страница подборки"""
    author = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    is_added = serializers.SerializerMethodField(default=False)
    count_ratings = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = (
            'path', 'title', 'author', 'description', 'wallpaper', 'image_url', 'members_amount', 'rating', 'courses',
            'is_added', 'count_ratings', 'grade')

    @staticmethod
    def get_author(collection):
        """Вернет автора"""
        return ProfileAsAuthor(collection.profile).data

    def get_courses(self, collection):
        """Вернет все курсы"""
        courses_to_collection = ProfileCourseCollection.objects.filter(collection=collection)
        courses = list()
        for item in courses_to_collection:
            if item.course.status.name == Util.COURSE_STATUS_RELEASE_NAME:
                courses.append(MiniCourseSerializer(item.course, context={'profile': self.context.get('profile')}).data)
        return courses

    def get_is_added(self, collection):
        """Добавлена ли подборка"""
        return HelperCollectionSerializer.get_is_added(collection=collection, profile=self.context.get('profile'))

    @staticmethod
    def get_count_ratings(collection):
        """Количество оценок подборки"""
        return GradeCollectionSerializer.get_count_star(collection=collection)

    def get_grade(self, collection):
        profile_collection_queryset = ProfileCollection.objects.filter(collection=collection,
                                                                       profile=self.context.get('profile'))
        if len(profile_collection_queryset) == 0:
            return None
        return profile_collection_queryset[0].grade


class WindowDetailCollectionSerializer(serializers.ModelSerializer):
    """SERIALIZER. Окно изменения данных подборки"""

    class Meta:
        model = Collection
        fields = ('title', 'description', 'wallpaper', 'image_url', 'path')

    def create(self, validated_data):
        """Создание"""
        return Collection.objects.create(**validated_data, profile=self.context.get('profile'))

    def update(self, instance, validated_data):
        """Обновление"""
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)

        # Изменение картинок
        instance.wallpaper = validated_data.get('wallpaper', instance.wallpaper)
        new_image = validated_data.get('image_url', -1)
        if new_image != -1:
            update_image = Util.get_image(old=instance.image_url, new=new_image,
                                          default=Util.DEFAULT_IMAGES.get('collection'))
            instance.image_url = Util.get_update_image(old=instance.image_url, new=update_image)

        instance.save()
        return instance


#####################################

# #########################################
#        ######## GRADE ########
# #########################################

class GradeCollectionSerializer(serializers.ModelSerializer):
    """SERIALIZER. Оценка подборки"""

    class Meta:
        model = ProfileCollection
        fields = ('grade',)

    @staticmethod
    def get_count_star(collection):
        """Количество оценок"""
        stars = CollectionStars.objects.get(collection=collection)
        return stars.one_stars_count + stars.two_stars_count + stars.three_stars_count + stars.four_stars_count + stars.five_stars_count

    @staticmethod
    def add_collection_star(collection, grade):
        """Добавить оценку"""
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
        """Убрать оценку"""
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
        """Обновить оценку"""
        stars = CollectionStars.objects.get(collection=collection)

        sum_grade = stars.one_stars_count + stars.two_stars_count * 2 + stars.three_stars_count * 3 \
                    + stars.four_stars_count * 4 + stars.five_stars_count * 5
        count = stars.one_stars_count + stars.two_stars_count + stars.three_stars_count + stars.four_stars_count \
                + stars.five_stars_count

        rating = 0
        if count != 0:
            rating = sum_grade / count
        collection.rating = rating
        collection.save()

    @staticmethod
    def has_grade(collection, profile):
        profile_collection_queryset = ProfileCollection.objects.filter(profile=profile, collection=collection)
        has_grade_local = False
        if len(profile_collection_queryset):
            has_grade_local = profile_collection_queryset[0].grade is not None
        return has_grade_local

    def create(self, validated_data):
        """Создание оценки"""

        profile_collection_queryset = ProfileCollection.objects.filter(profile=self.context.get('profile'),
                                                                       collection=self.context.get('collection'))
        if not len(profile_collection_queryset):
            profile_collection = ProfileCollection.objects.create(profile=self.context.get('profile'),
                                                                  collection=self.context.get('collection'),
                                                                  date_added=None)
        else:
            profile_collection = profile_collection_queryset[0]
        if profile_collection.grade is not None:
            raise serializers.ValidationError({'grade': 'Вы уже оценивали подборку'})

        profile_collection.grade = validated_data['grade']
        self.add_collection_star(collection=profile_collection.collection, grade=profile_collection.grade)
        self.update_rating_collection(collection=profile_collection.collection)
        profile_collection.save()
        return profile_collection

    def update(self, instance, validated_data):
        """Обновление оценки"""
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
        """Удаление оценки"""
        profile_collection = self.context.get('profile_collection')
        if profile_collection.grade is not None:
            self.difference_collection_star(collection=profile_collection.collection, grade=profile_collection.grade)
            self.update_rating_collection(collection=profile_collection.collection)
            profile_collection.grade = None
            profile_collection.save()
        return profile_collection
