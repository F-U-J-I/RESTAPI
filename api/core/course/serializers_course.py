from bs4 import BeautifulSoup
from rest_framework import serializers
from rest_framework.utils import json

from core.collection.models_collection import Collection
from .models_course import Course, ProfileCourse, Theme, Lesson, \
    Step, ProfileStep, \
    CourseInfo, CourseMainInfo, CourseFit, CourseSkill, CourseStars, ProfileTheme, ProfileLesson, ProfileActionsLogs, \
    ProfileCourseCollection
#####################################
#         ##  COURSE ##
#####################################
from ..profile.serializers_profile import ProfileAsAuthor
from ..service.parse_html.parse_html import ParseHtml
from ..utils import Util


class HelperCourseSerializer:
    """Помощник сериализации """

    @staticmethod
    def get_is_added(course, profile):
        """Добавлен ли"""
        profile_to_course = ProfileCourse.objects.filter(course=course, profile=profile)
        if profile_to_course:
            return True
        return False

    @staticmethod
    def get_status_progress(course, profile):
        """Вернуть статус курса"""
        profile_to_course = ProfileCourse.objects.filter(course=course, profile=profile)
        if len(profile_to_course) != 0:
            status = profile_to_course[0].status
            if status is not None:
                return status.name
        return None


class MaxProgressUpdater:
    """Обновитель максимального прогресса"""

    @staticmethod
    def update_max_progress(old, new, step=None, lesson=None, theme=None, course=None):
        """Обновить максимальный прогресс"""
        diff_max_progress = new - old

        generate_lesson = None
        if step is not None:
            MaxProgressUpdater.update_max_progress_step(step=step, diff_max_progress=diff_max_progress)
            generate_lesson = step.lesson

        generate_theme = None
        if lesson is None:
            lesson = generate_lesson
        if lesson is not None:
            MaxProgressUpdater.update_max_progress_lesson(lesson=lesson, diff_max_progress=diff_max_progress)
            generate_theme = lesson.theme

        generate_course = None
        if theme is None:
            theme = generate_theme
        if theme is not None:
            MaxProgressUpdater.update_max_progress_theme(theme=theme, diff_max_progress=diff_max_progress)
            generate_course = theme.course

        if course is None:
            course = generate_course
        if course is not None:
            MaxProgressUpdater.update_max_progress_course(course=course, diff_max_progress=diff_max_progress)

    @staticmethod
    def update_max_progress_course(course, diff_max_progress):
        """Обновить максимальный прогресс курса"""
        course.max_progress += diff_max_progress
        course.save()

    @staticmethod
    def update_max_progress_theme(theme, diff_max_progress):
        """Обновить максимальный прогресс темы"""
        theme.max_progress += diff_max_progress
        theme.save()

    @staticmethod
    def update_max_progress_lesson(lesson, diff_max_progress):
        """Обновить максимальный урока"""
        lesson.max_progress += diff_max_progress
        lesson.save()

    @staticmethod
    def update_max_progress_step(step, diff_max_progress):
        """Обновить максимальный прогресс шага"""
        step.max_progress += diff_max_progress
        step.save()


class ProgressUpdater:
    """Обновитель прогресса"""

    @staticmethod
    def get_or_create(model, validation_data):
        """Вернуть или создать"""
        queryset = model.objects.filter(**validation_data)
        if len(queryset) == 0:
            return model.objects.create(**validation_data)
        return queryset[0]

    @staticmethod
    def update_progress(old, new, profile_step=None, profile_lesson=None, profile_theme=None, profile_course=None):
        """Обновить прогресс"""
        diff_progress = new - old

        generate_lesson = None
        if profile_step is not None:
            ProgressUpdater.update_progress_step(profile_step=profile_step, diff_progress=diff_progress)
            data = {'lesson': profile_step.step.lesson, 'profile': profile_step.profile}
            generate_lesson = ProgressUpdater.get_or_create(model=ProfileLesson, validation_data=data)

        generate_theme = None
        if profile_lesson is None:
            profile_lesson = generate_lesson
        if profile_lesson is not None:
            ProgressUpdater.update_progress_lesson(profile_lesson=profile_lesson, diff_progress=diff_progress)
            data = {'theme': profile_step.step.lesson.theme, 'profile': profile_step.profile}
            generate_theme = ProgressUpdater.get_or_create(model=ProfileTheme, validation_data=data)

        generate_course = None
        if profile_theme is None:
            profile_theme = generate_theme
        if profile_theme is not None:
            ProgressUpdater.update_progress_theme(profile_theme=profile_theme, diff_progress=diff_progress)
            data = {'course': profile_step.step.lesson.theme.course, 'profile': profile_step.profile}
            generate_course = ProgressUpdater.get_or_create(model=ProfileCourse, validation_data=data)

        if profile_course is None:
            profile_course = generate_course
        if profile_course is not None:
            ProgressUpdater.update_progress_course(profile_course=profile_course, diff_progress=diff_progress)

    @staticmethod
    def update_progress_course(profile_course, diff_progress):
        """Обновить прогресс курса"""
        profile_course.progress += diff_progress
        profile_course.save()

    @staticmethod
    def update_progress_theme(profile_theme, diff_progress):
        """Обновить прогресс темы"""
        profile_theme.progress += diff_progress
        profile_theme.save()

    @staticmethod
    def update_progress_lesson(profile_lesson, diff_progress):
        """Обновить прогресс урока"""
        profile_lesson.progress += diff_progress
        profile_lesson.save()

    @staticmethod
    def update_progress_step(profile_step, diff_progress):
        """Обновить прогресс шага"""
        profile_step.progress += diff_progress
        profile_step.save()


class BriefCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('path', 'title', 'image_url')


class CourseSerializer(serializers.ModelSerializer):
    """SERIALIZER. Курс"""
    author = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()

    status_progress = serializers.SerializerMethodField(default=None)
    progress = serializers.SerializerMethodField(default=None)

    class Meta:
        model = Course
        fields = (
            'path', 'title', 'description', 'author', 'image_url', 'duration_in_minutes', 'rating', 'members_amount',
            'price', 'collection', 'status_progress', 'progress')

    @staticmethod
    def get_author(course):
        """Вернуть автора"""
        return ProfileAsAuthor(course.profile).data

    def get_collection(self, course):
        profile = self.context.get('profile')
        if profile is None:
            return None
        collection_queryset = ProfileCourseCollection.objects.filter(course=course)
        profile_collection_list = collection_queryset.filter(profile=profile)
        profile_added = [BriefCollectionSerializer(_.collection).data for _ in profile_collection_list]
        return {
            'profile_added': profile_added,
            'quantity_in_collection': len(collection_queryset)
        }

    def get_status_progress(self, course):
        """Вернуть статус прогресса"""
        if self.context.get('profile', None) is None:
            return None
        return HelperCourseSerializer.get_status_progress(course=course, profile=self.context.get('profile'))

    def get_progress(self, course):
        """Вернуть прогресс"""
        if self.context.get('profile', None) is None:
            return None
        profile_course_list = ProfileCourse.objects.filter(course=course, profile=self.context.get('profile'))
        if len(profile_course_list) == 0:
            return None
        return {
            'progress': profile_course_list[0].progress,
            'max_progress': course.max_progress,
        }


class MiniCourseSerializer(serializers.ModelSerializer):
    """SERIALIZER. Мини курс"""
    author = serializers.SerializerMethodField()
    status_progress = serializers.SerializerMethodField(default=None)
    progress = serializers.SerializerMethodField(default=None)

    class Meta:
        model = Course
        fields = (
            'path', 'title', 'description', 'author', 'image_url', 'duration_in_minutes', 'rating', 'members_amount',
            'price', 'status_progress', 'progress')

    @staticmethod
    def get_author(course):
        """Вернуть автора"""
        return ProfileAsAuthor(course.profile).data

    def get_status_progress(self, course):
        """Вернуть статус прогресса"""
        if self.context.get('profile', None) is None:
            return None
        return HelperCourseSerializer.get_status_progress(course=course, profile=self.context.get('profile'))

    def get_progress(self, course):
        """Вернуть прогресс"""
        if self.context.get('profile', None) is None:
            return None
        profile_course_list = ProfileCourse.objects.filter(course=course, profile=self.context.get('profile'))
        if len(profile_course_list) == 0:
            return None
        return {
            'progress': profile_course_list[0].progress,
            'max_progress': course.max_progress,
        }


class CourseShortInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ('path', 'title', 'description', 'image_url')


class PageCourseSerializer(serializers.ModelSerializer):
    """SERIALIZER. Детальная страница курса"""

    author = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    status_progress = serializers.SerializerMethodField(default=None)

    class Meta:
        model = Course
        fields = ('path', 'title', 'author', 'image_url', 'price', 'duration_in_minutes', 'rating', 'members_amount',
                  'status_progress')

    @staticmethod
    def get_author(course):
        """Вернуть автора"""
        return ProfileAsAuthor(course.profile).data

    def get_rating(self, course):
        stars = CourseStars.objects.get(course=course)
        reviews_count = stars.one_stars_count + stars.two_stars_count + stars.three_stars_count + stars.four_stars_count + stars.five_stars_count
        queryset = ProfileCourse.objects.filter(course=course, profile=self.context.get('profile'))
        grade = None
        if len(queryset) != 0:
            grade = queryset[0].grade
        return {
            'value': course.rating,
            'grade': grade,
            'reviews_count': reviews_count,
        }

    def get_status_progress(self, course):
        """Вернуть статус прогресса"""
        return HelperCourseSerializer.get_status_progress(course=course, profile=self.context.get('profile'))


class PageInfoCourseSerializer(serializers.ModelSerializer):
    """SERIALIZER. Страница курса """

    main_info = serializers.SerializerMethodField()
    fits = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()

    class Meta:
        model = CourseInfo
        fields = ('main_info', 'fits', 'skills', 'stars')

    @staticmethod
    def get_main_info(course_info):
        """Вернуть главную информацию"""
        main_info_list = CourseMainInfo.objects.filter(course_info=course_info)
        if len(main_info_list) == 0:
            return None
        main_info = main_info_list[0]
        title_image_url = None
        if main_info.title_image_url:
            title_image_url = main_info.title_image_url.url
        return {
            'title_image_url': title_image_url,
            'goal_description': main_info.goal_description
        }

    @staticmethod
    def get_fits(course_info):
        """Вернуть представителей"""
        filter_fits = CourseFit.objects.filter(course_info=course_info)
        fits = list()
        for fit in filter_fits:
            fits.append({
                'title': fit.title,
                'description': fit.description
            })
        return fits

    @staticmethod
    def get_skills(course_info):
        """Вернуть навыки"""
        filter_skills = CourseSkill.objects.filter(course_info=course_info)
        skills = list()
        for skill in filter_skills:
            skills.append(skill.name)
        return skills

    @staticmethod
    def get_stars(course_info):
        """Вернуть рейтинг"""
        stars = CourseStars.objects.get(course=course_info.course)
        stars_dict = {
            'five': stars.five_stars_count,
            'four': stars.four_stars_count,
            'three': stars.three_stars_count,
            'two': stars.two_stars_count,
            'one': stars.one_stars_count,
        }
        stars_dict['total_number'] = sum(stars_dict.values())
        return stars_dict


class PageThemesCourseSerializer(serializers.ModelSerializer):
    """SERIALIZER. Страница курса """

    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Theme
        fields = ('title', 'lessons')

    @staticmethod
    def get_lessons(theme):
        queryset = Lesson.objects.filter(theme=theme)
        lessons = [_.title for _ in queryset]
        return lessons


class CourseEditSerializer(serializers.ModelSerializer):
    """SERIALIZER. Окно изменения курса"""

    class Meta:
        model = Course
        fields = ('title', 'image_url', 'description')


class EditPageInfoCourseSerializer(serializers.ModelSerializer):
    """SERIALIZER. Изменение страницы курса"""

    course = serializers.SerializerMethodField()
    main_info = serializers.SerializerMethodField()
    fits = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = CourseInfo
        fields = ('course', 'main_info', 'fits', 'skills')

    @staticmethod
    def get_course(course_info):
        """Вернет курс"""
        return CourseEditSerializer(course_info.course).data

    @staticmethod
    def get_main_info(course_info):
        """Вернуть главную информацию"""
        main_info_list = CourseMainInfo.objects.filter(course_info=course_info)
        if len(main_info_list) == 0:
            return None
        main_info = main_info_list[0]
        title_image_url = None
        if main_info.title_image_url:
            title_image_url = main_info.title_image_url.url
        return {
            'title_image_url': title_image_url,
            'goal_description': main_info.goal_description
        }

    @staticmethod
    def get_fits(course_info):
        """Вернуть представителей"""
        filter_fits = CourseFit.objects.filter(course_info=course_info)
        fits = list()
        for fit in filter_fits:
            fits.append({
                'pk': fit.pk,
                'title': fit.title,
                'description': fit.description
            })
        return fits

    @staticmethod
    def get_skills(course_info):
        """Вернуть навыки"""
        filter_skills = CourseSkill.objects.filter(course_info=course_info)
        skills = list()
        for skill in filter_skills:
            skills.append({
                'pk': skill.pk,
                'name': skill.name
            })
        return skills


class ActionCourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ()


class CourseFitSerializer(serializers.ModelSerializer):
    """SERIALIZER. Представитля"""

    class Meta:
        model = CourseFit
        fields = ('pk', 'title', 'description')

    def create(self, validated_data):
        """Создание представителя"""
        course_info = self.context.get('course_info')
        title = validated_data.get('title', None)
        description = validated_data.get('description', None)
        return CourseFit.objects.create(course_info=course_info, title=title, description=description)

    def update(self, instance, validated_data):
        """Обновление представителя"""
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class CourseSkillSerializer(serializers.ModelSerializer):
    """SERIALIZER. Навык """

    class Meta:
        model = CourseSkill
        fields = ('pk', 'name')

    def create(self, validated_data):
        """Создание навыка"""
        course_info = self.context.get('course_info')
        name = validated_data.get('name', None)
        return self.Meta.model.objects.create(course_info=course_info, name=name)

    def update(self, instance, validated_data):
        """Обновление навыка"""
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


#####################################


#####################################
#   ##  COURSE COMPLETION PAGE ##
#####################################


# PAGE THEMES
class CourseTitleSerializer(serializers.ModelSerializer):
    """SERIALIZER. Титульник курса"""

    class Meta:
        model = Course
        fields = ('path', 'title', 'image_url', 'description')


class ProfileThemeSerializer(serializers.ModelSerializer):
    """SERIALIZER. Профиль к теме"""
    count_lesson = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Theme
        fields = ('path', 'title', 'image_url', 'count_lesson', 'progress', 'is_complete')

    @staticmethod
    def get_count_lesson(theme):
        """Вернуть количество уроков в теме"""
        return len(Lesson.objects.filter(theme=theme))

    def get_progress(self, theme):
        """Вернуть прогресс над темой"""
        profile_theme_list = ProfileTheme.objects.filter(theme=theme, profile=self.context.get('profile'))
        if len(profile_theme_list) == 0:
            return None
        return {
            'progress': profile_theme_list[0].progress,
            'max_progress': theme.max_progress,
        }

    def get_is_complete(self, theme):
        """Завершена ли тема"""
        progress = self.get_progress(theme=theme)
        if (progress is not None) and (progress.get('progress') == progress.get('max_progress')):
            return True
        return False


class ActionThemeSerializer(serializers.ModelSerializer):
    """SERIALIZER. Действие над темой"""
    count_lesson = serializers.SerializerMethodField()

    class Meta:
        model = Theme
        fields = ('path', 'title', 'image_url', 'max_progress', 'count_lesson')

    @staticmethod
    def get_count_lesson(theme):
        """Вернуть количество уроков в теме"""
        return len(Lesson.objects.filter(theme=theme))

    def create(self, validated_data):
        """Создать действие над темой"""
        return Theme.objects.create(**validated_data, course=self.context.get('course'))

    def update(self, instance, validated_data):
        """Обновить действие над темой"""
        instance.title = validated_data.get('title', instance.title)

        new_path = validated_data.get('path', None)
        if new_path is not None:
            new_path = Util.get_update_path(new_path=new_path)
        instance.path = Util.get_new_path(new_path=new_path, old_path=instance.path, model=Theme)

        new_image = validated_data.get('image_url', -1)
        if new_image != -1:
            update_image = Util.get_image(old=instance.image_url, new=new_image,
                                          default=Util.DEFAULT_IMAGES.get('lesson'))
            instance.image_url = Util.get_update_image(old=instance.image_url, new=update_image)

        instance.save()
        return instance


# PAGE LESSONS
class ThemeTitleSerializer(serializers.ModelSerializer):
    """SERIALIZER. Титульник темы"""

    class Meta:
        model = Theme
        fields = ('path', 'title', 'image_url')


class ProfileLessonSerializer(serializers.ModelSerializer):
    """SERIALIZER. Профиль к уроку"""
    count_step = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField(default=False)
    current_step = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ('path', 'title', 'image_url', 'current_step', 'count_step', 'progress', 'is_complete')

    @staticmethod
    def get_count_step(lesson):
        """Вернуть количество шагов в уроке"""
        return len(Step.objects.filter(lesson=lesson))

    def get_progress(self, lesson):
        """Вернуть прогресс"""
        profile_lesson_list = ProfileLesson.objects.filter(lesson=lesson, profile=self.context.get('profile'))
        if len(profile_lesson_list) == 0:
            return None
        return {
            'progress': profile_lesson_list[0].progress,
            'max_progress': lesson.max_progress,
        }

    def get_is_complete(self, lesson):
        """Завершен ли урок"""
        progress = self.get_progress(lesson=lesson)
        if (progress is not None) and (progress.get('progress') == progress.get('max_progress')):
            return True
        return False

    def get_link(self):
        """Вернуть ссылку на урок"""
        link_old = self.context.get('request').build_absolute_uri()
        return "/".join(link_old.split('/')[:-1])

    @staticmethod
    def get_current_step(lesson):
        """Текуший шаг"""
        step_list = Step.objects.filter(lesson=lesson)
        if len(step_list) == 0:
            return None
        logs = ProfileActionsLogs.objects.filter(step__in=step_list)
        if len(logs) == 0:
            # return f"{self.get_link()}/{lesson.path}/steps/{step_list[0].path}"
            return step_list[0].path
        current_step = logs[0]
        last_date = current_step.date_action
        for log in logs:
            if log.date_action > last_date:
                last_date = log.date_action
                current_step = log
        # return f"{self.get_link()}/{lesson.path}/steps/{current_step.step.path}"
        return current_step.step.path

    @staticmethod
    def get_image_url(lesson):
        return Util.get_link_image(lesson.image_url.url)


class ActionLessonSerializer(serializers.ModelSerializer):
    """SERIALIZER. Действия над уроком"""
    count_step = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ('title', 'image_url', 'max_progress', 'count_step', 'path')

    @staticmethod
    def get_count_step(lesson):
        """Вернуть количество шагов в уроке"""
        return len(Step.objects.filter(lesson=lesson))

    def create(self, validated_data):
        """Создать урок"""
        return Lesson.objects.create(**validated_data, theme=self.context.get('theme'))

    def update(self, instance, validated_data):
        """Обновить урок"""
        instance.title = validated_data.get('title', instance.title)

        new_image = validated_data.get('image_url', -1)
        if new_image != -1:
            update_image = Util.get_image(old=instance.image_url, new=new_image,
                                          default=Util.DEFAULT_IMAGES.get('lesson'))
            instance.image_url = Util.get_update_image(old=instance.image_url, new=update_image)

        instance.save()
        return instance


# PAGE STEPS
class GetStepSerializer(serializers.ModelSerializer):
    """SERIALIZER. Шаг"""
    is_active = serializers.SerializerMethodField(default=False)
    is_complete = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Step
        fields = ('path', 'is_active', 'is_complete')

    def get_is_active(self, step):
        """Текущий шаг"""
        if step == self.context.get('current_step'):
            return True
        return False

    def get_is_complete(self, step):
        """Завешен ли шаг"""
        profile_step_list = ProfileStep.objects.filter(step=step, profile=self.context.get('profile'))
        if len(profile_step_list) == 0:
            return False
        if profile_step_list[0].status.name == Util.PROFILE_COURSE_STATUS_STUDIED_NAME:
            return True
        return False

    def update(self, instance, validated_data):
        """Обновить страницу с шагом"""
        new_status = self.context.get('status', None)
        new_progress = self.context.get('progress', None)

        if (new_status is not None) and (instance.status != new_status):
            instance.status = new_status
            if new_status.name == Util.PROFILE_COURSE_STATUS_STUDIED_NAME:
                new_progress = instance.step.max_progress

        if (new_progress is not None) and (new_progress != instance.progress):
            ProgressUpdater.update_progress(old=instance.progress, new=new_progress, profile_step=instance)

        instance.save()
        return instance


class ProfileStepSerializer(serializers.ModelSerializer):
    """SERIALIZER. Профиль к шагу"""
    path_step = serializers.SerializerMethodField()
    path_profile = serializers.SerializerMethodField()

    class Meta:
        model = ProfileStep
        fields = ('path_step', 'path_profile', 'status', 'progress')

    @staticmethod
    def get_path_step(profile_step):
        """Вернуть путь к шагу"""
        return profile_step.step.path

    @staticmethod
    def get_path_profile(profile_step):
        """Вернуть путь к профилю"""
        return profile_step.profile.path

    @staticmethod
    def get_status(profile_step):
        """Вернуть статус"""
        return profile_step.status.name

    def update(self, instance, validated_data):
        """Обновить шаг к профилю"""
        new_status = self.context.get('status', None)
        new_progress = self.context.get('progress', None)

        if (new_status is not None) and (new_status != instance.status):
            instance.status = new_status
            if new_status.name == Util.PROFILE_COURSE_STATUS_STUDIED_NAME:
                new_progress = instance.step.max_progress

        if (new_progress is not None) and (new_progress != instance.progress):
            ProgressUpdater.update_progress(old=instance.progress, new=new_progress, profile_step=instance)

        instance.save()
        return instance


class StepSerializer(serializers.ModelSerializer):
    """SERIALIZER. Шаг"""
    is_complete = serializers.SerializerMethodField(default=False)
    prev = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()

    class Meta:
        model = Step
        fields = ('path', 'number', 'title', 'content', 'is_complete', 'prev', 'next')

    def get_is_complete(self, step):
        """Заверешен ли курс"""
        profile_step_list = ProfileStep.objects.filter(step=step, profile=self.context.get('profile'))
        if len(profile_step_list) == 0:
            return False
        if profile_step_list[0].status.name == Util.PROFILE_COURSE_STATUS_STUDIED_NAME:
            return True
        return False

    def get_link(self):
        """Вернуть ссылку"""
        link_old = self.context.get('request').build_absolute_uri()
        return "/".join(link_old.split('/')[:-2])

    def get_prev(self, step):
        """Вернуть ссылку на предыдущий шаг"""
        if step.number == 1:
            return None
        step_prev = Step.objects.get(lesson=self.context.get('lesson'), number=step.number - 1)
        return f"{self.get_link()}/{step_prev.path}"

    def get_next(self, step):
        """Вернуть ссылку на следующий шаг"""
        if step.number == len(Step.objects.filter(lesson=step.lesson)):
            return None
        step_next = Step.objects.get(number=step.number + 1)
        return f"{self.get_link()}/{step_next.path}"





class StepContentSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = Step
        fields = ('content', )

    @staticmethod
    def get_content(step):
        return ParseHtml(step.content).parse()


class AndroidStepSerializer(serializers.ModelSerializer):
    """SERIALIZER. Шаг"""
    is_complete = serializers.SerializerMethodField(default=False)
    prev = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()

    class Meta:
        model = Step
        fields = ('path', 'title', 'content_json', 'is_complete', 'prev', 'next')

    def get_is_complete(self, step):
        """Завершен ли курс"""
        profile_step_list = ProfileStep.objects.filter(step=step, profile=self.context.get('profile'))
        if len(profile_step_list) == 0:
            return False
        if profile_step_list[0].status.name == Util.PROFILE_COURSE_STATUS_STUDIED_NAME:
            return True
        return False

    def get_link(self):
        """Вернуть ссылку"""
        link_old = self.context.get('request').build_absolute_uri()
        return "/".join(link_old.split('/')[:-2])

    def get_prev(self, step):
        """Вернуть ссылку на предыдущий шаг"""
        if step.number == 1:
            return None
        step_prev = Step.objects.get(number=step.number - 1)
        return f"{self.get_link()}/{step_prev.path}"

    def get_next(self, step):
        """Вернуть ссылку на следующий шаг"""
        if step.number == len(Step.objects.filter(lesson=step.lesson)):
            return None
        step_next = Step.objects.get(number=step.number + 1)
        return f"{self.get_link()}/{step_next.path}"


class ActionStepSerializer(serializers.ModelSerializer):
    """SERIALIZER. Действия над шагом"""

    class Meta:
        model = Step
        fields = ('title', 'content', 'max_progress', 'path')

    @staticmethod
    def update_numbers(step_list):
        """Обновить номер шага"""
        for i in range(len(step_list)):
            step_list[i].number = i + 1
            step_list[i].save()

    def create(self, validated_data):
        """Создание шага"""
        lesson = self.context.get('lesson')
        number = self.context.get('number')
        step = Step.objects.create(**validated_data, lesson=lesson, number=number)
        MaxProgressUpdater.update_max_progress(old=0, new=1, step=step)
        return step

    def update(self, instance, validated_data):
        """Обновить шаг"""
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)

        new_max_progress = validated_data.get('max_progress', None)
        if (new_max_progress is not None) and (new_max_progress != instance.max_progress):
            MaxProgressUpdater.update_max_progress(old=instance.max_progress, new=new_max_progress, step=instance)

        instance.save()
        return instance


# #########################################
#        ######## GRADE ########
# #########################################

class GradeCourseSerializer(serializers.ModelSerializer):
    """SERIALIZER. Оценки курса"""

    class Meta:
        model = ProfileCourse
        fields = ('grade',)

    @staticmethod
    def add_course_star(course, grade):
        """Добавить оценку курсу"""
        stars = CourseStars.objects.get(course=course)
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
    def difference_course_star(course, grade):
        """Убрать оценку у курса"""
        stars = CourseStars.objects.get(course=course)
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
    def update_rating_course(course):
        """Обновить рейтинг курса"""
        stars = CourseStars.objects.get(course=course)

        sum_grade = stars.one_stars_count + stars.two_stars_count * 2 + stars.three_stars_count * 3 \
                    + stars.four_stars_count * 4 + stars.five_stars_count * 5
        count = stars.one_stars_count + stars.two_stars_count + stars.three_stars_count + stars.four_stars_count \
                + stars.five_stars_count
        try:
            rating = sum_grade / count
        except ZeroDivisionError:
            rating = 0
        course.rating = rating
        course.save()

    def create(self, validated_data):
        """Создание оценки"""
        profile_course = ProfileCourse.objects.get(profile=self.context.get('profile'),
                                                   course=self.context.get('course'))
        if profile_course.grade is not None:
            raise serializers.ValidationError({'grade': 'Вы уже оценивали курс'})

        profile_course.grade = validated_data['grade']
        self.add_course_star(course=profile_course.course, grade=profile_course.grade)
        self.update_rating_course(course=profile_course.course)
        profile_course.save()
        return profile_course

    def update(self, instance, validated_data):
        """Обновление оценки"""
        grade_list = (1, 2, 3, 4, 5)
        new_grade = validated_data.get('grade')
        if (type(new_grade) == int) and (new_grade in grade_list) and (instance.grade != new_grade):
            self.difference_course_star(course=instance.course, grade=instance.grade)
            instance.grade = validated_data.get('grade')
            instance.save()
            self.add_course_star(course=instance.course, grade=instance.grade)
            self.update_rating_course(course=instance.course)
        return instance

    def delete_grade(self):
        """Удаление оценки"""
        profile_course = self.context.get('profile_course')
        if profile_course.grade is not None:
            self.difference_course_star(course=profile_course.course, grade=profile_course.grade)
            self.update_rating_course(course=profile_course.course)
            profile_course.grade = None
            profile_course.save()
        return profile_course
