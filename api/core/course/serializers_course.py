from rest_framework import serializers

from .models_course import Course, ProfileCourse, Theme, Lesson, \
    Step, ProfileStep, \
    CourseInfo, CourseMainInfo, CourseFit, CourseSkill, CourseStars, ProfileTheme, ProfileLesson, ProfileActionsLogs
#####################################
#         ##  COURSE ##
#####################################
from ..utils import Util


class HelperCourseSerializer:
    @staticmethod
    def get_is_added(course, profile):
        profile_to_course = ProfileCourse.objects.filter(course=course, profile=profile)
        if profile_to_course:
            return True
        return False

    @staticmethod
    def get_status_progress(course, profile):
        profile_to_course = ProfileCourse.objects.filter(course=course, profile=profile)
        if len(profile_to_course) != 0:
            status = profile_to_course[0].status
            if status is not None:
                return status.name
        return None

    @staticmethod
    def get_progress(course, profile):
        if HelperCourseSerializer.get_status_progress(course, profile) is None:
            return None

        max_progress = 0
        progress = 0
        for theme in Theme.objects.filter(course=course):
            for lesson in Lesson.objects.filter(theme=theme):
                for step in Step.objects.filter(lesson=lesson):
                    profile_step = ProfileStep.objects.filter(step=step, profile=profile)
                    if profile_step:
                        max_progress += step.max_progress
                        progress += profile_step.mark
        return {
            'max_progress': max_progress,
            'progress': progress
        }

    @staticmethod
    def get_progress_theme(theme, profile):
        max_progress = 0
        progress = 0
        for lesson in Lesson.objects.filter(theme=theme):
            for step in Step.objects.filter(lesson=lesson):
                profile_step = ProfileStep.objects.filter(step=step, profile=profile)
                if profile_step:
                    progress += profile_step.mark
                max_progress += step.max_progress
        return {
            'max_progress': max_progress,
            'progress': progress
        }


class MaxProgressUpdater:
    @staticmethod
    def update_max_progress(old, new, step=None, lesson=None, theme=None, course=None):
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
        course.max_progress += diff_max_progress
        course.save()

    @staticmethod
    def update_max_progress_theme(theme, diff_max_progress):
        theme.max_progress += diff_max_progress
        theme.save()

    @staticmethod
    def update_max_progress_lesson(lesson, diff_max_progress):
        lesson.max_progress += diff_max_progress
        lesson.save()

    @staticmethod
    def update_max_progress_step(step, diff_max_progress):
        step.max_progress += diff_max_progress
        step.save()


class CourseSerializer(serializers.ModelSerializer):
    """курс"""
    author = serializers.SerializerMethodField()
    quantity_in_collection = serializers.SerializerMethodField()

    status_progress = serializers.SerializerMethodField(default=None)
    progress = serializers.SerializerMethodField(default=None)

    class Meta:
        model = Course
        fields = (
            'path', 'title', 'description', 'author', 'image_url', 'duration_in_minutes', 'rating', 'members_amount',
            'quantity_in_collection', 'status_progress', 'progress')

    @staticmethod
    def get_author(course):
        return course.profile.user.username

    def get_quantity_in_collection(self, course):
        if self.context.get('profile', None) is None:
            return None
        return len(ProfileCourse.objects.filter(course=course, profile=self.context.get('profile')))

    def get_status_progress(self, course):
        if self.context.get('profile', None) is None:
            return None
        return HelperCourseSerializer.get_status_progress(course=course, profile=self.context.get('profile'))

    def get_progress(self, course):
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
    """Мини курс"""
    author = serializers.SerializerMethodField()
    status_progress = serializers.SerializerMethodField(default=None)
    progress = serializers.SerializerMethodField(default=None)

    class Meta:
        model = Course
        fields = (
            'path', 'title', 'description', 'author', 'image_url', 'duration_in_minutes', 'rating', 'members_amount',
            'status_progress', 'progress')

    @staticmethod
    def get_author(course):
        return course.profile.user.username

    def get_status_progress(self, course):
        if self.context.get('profile', None) is None:
            return None
        return HelperCourseSerializer.get_status_progress(course=course, profile=self.context.get('profile'))

    def get_progress(self, course):
        if self.context.get('auth', None) is None:
            return None
        profile_course_list = ProfileCourse.objects.filter(course=course, profile=self.context.get('auth'))
        if len(profile_course_list) == 0:
            return None
        return {
            'progress': profile_course_list[0].progress,
            'max_progress': course.max_progress,
        }


class PageCourseSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    status_progress = serializers.SerializerMethodField(default=None)

    class Meta:
        model = Course
        fields = ('title', 'author', 'image_url', 'duration_in_minutes', 'rating', 'members_amount',
                  'status_progress')

    @staticmethod
    def get_author(course):
        return course.profile.user.username

    def get_status_progress(self, course):
        return HelperCourseSerializer.get_status_progress(course=course, profile=self.context.get('profile'))


class PageInfoCourseSerializer(serializers.ModelSerializer):
    main_info = serializers.SerializerMethodField()
    fits = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()

    class Meta:
        model = CourseInfo
        fields = ('main_info', 'fits', 'skills', 'stars')

    @staticmethod
    def get_main_info(course_info):
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
        filter_skills = CourseSkill.objects.filter(course_info=course_info)
        skills = list()
        for skill in filter_skills:
            skills.append(skill.name)
        return skills

    @staticmethod
    def get_stars(course_info):
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


class CourseEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('title', 'image_url', 'description')


class EditPageInfoCourseSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    main_info = serializers.SerializerMethodField()
    fits = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()

    class Meta:
        model = CourseInfo
        fields = ('course', 'main_info', 'fits', 'skills', 'stars')

    @staticmethod
    def get_main_info(course_info):
        return CourseEditSerializer(course_info.course)

    @staticmethod
    def get_main_info(course_info):
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
        filter_skills = CourseSkill.objects.filter(course_info=course_info)
        skills = list()
        for skill in filter_skills:
            skills.append({
                'pk': skill.pk,
                'title': skill.name
            })
        return skills

    @staticmethod
    def get_stars(course_info):
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


class CourseFitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFit
        fields = ('pk', 'title', 'description')

    def create(self, validated_data):
        course_info = self.context.get('course_info')
        title = validated_data.get('title', None)
        description = validated_data.get('description', None)
        return CourseFit.objects.create(course_info=course_info, title=title, description=description)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class ActionPageInfoCourseSerializer(serializers.ModelSerializer):
    course_info = serializers.SerializerMethodField()
    main_info = serializers.SerializerMethodField()
    fits = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()

    class Meta:
        model = CourseInfo
        fields = ('course_info', 'main_info', 'fits', 'skills', 'stars')

    def update_course(self, instance, validated_data):
        if validated_data is None:
            return None

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)

        new_image = validated_data.get('image_url', -1)
        if new_image != -1:
            update_image = Util.get_image(old=instance.image_url, new=new_image,
                                          default=Util.DEFAULT_IMAGES.get('course'))
            instance.image_url = Util.get_update_image(old=instance.image_url, new=update_image)

        instance.save()

    def update_main_info(self, instance, validated_data):
        if validated_data is None:
            return None

        instance.goal_description = validated_data.get('goal_description', instance.goal_description)

        new_image = validated_data.get('title_image_url', -1)
        if new_image != -1:
            instance.title_image_url = Util.get_update_image(old=instance.title_image_url, new=new_image)

        instance.save()

    def update_fits(self, fit_list, validated_data, course_info):
        if validated_data is None:
            return None

        for fit in validated_data:
            fit_pk = fit.get('pk', None)
            if fit_pk is None:
                curr_fit = CourseFit.objects.create(course_info=course_info)
                curr_fit.is_valid(raise_exception=True)
            else:
                curr_fit = fit_list.filter(pk=fit_pk)

            if fit.get('title', -1) != -1:
                curr_fit.title = fit.get('title')
            if fit.get('description', -1) != -1:
                curr_fit.description = fit.get('description')
            curr_fit.save()

    def update(self, instance, validated_data):
        course = instance.course
        self.update_course(instance=course, validated_data=validated_data.get('course', None))

        course_main_info = CourseMainInfo.objects.get(course_info=instance)
        self.update_main_info(instance=course_main_info, validated_data=validated_data.get('main_info', None))

        course_fit_list = CourseFit.objects.filter(course_info=instance)
        self.update_fits(fit_list=course_fit_list, course_info=instance,
                         validated_data=validated_data.get('fits', None))

        course_skill_list = CourseSkill.objects.filter(course_info=instance)


#####################################


#####################################
#   ##  COURSE COMPLETION PAGE ##
#####################################


# PAGE THEMES
class CourseTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ('path', 'title', 'image_url')


class ProfileThemeSerializer(serializers.ModelSerializer):
    count_lesson = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Theme
        fields = ('path', 'title', 'image_url', 'count_lesson', 'progress', 'is_complete')

    def get_count_lesson(self, theme):
        return len(Lesson.objects.filter(theme=theme))

    def get_progress(self, theme):
        profile_theme_list = ProfileTheme.objects.filter(theme=theme, profile=self.context.get('profile'))
        if len(profile_theme_list) == 0:
            return None
        return {
            'progress': profile_theme_list[0].progress,
            'max_progress': theme.max_progress,
        }

    def get_is_complete(self, theme):
        progress = self.get_progress(theme=theme)
        if (progress is not None) and (progress.get('progress') == progress.get('max_progress')):
            return True
        return False


class ActionThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ('title', 'image_url', 'max_progress', 'path')

    def create(self, validated_data):
        return Theme.objects.create(**validated_data, course=self.context.get('course'))

    def update(self, instance, validated_data):
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
    class Meta:
        model = Theme
        fields = ('path', 'title', 'image_url')


class ProfileLessonSerializer(serializers.ModelSerializer):
    count_step = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField(default=False)
    current_step = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ('path', 'title', 'image_url', 'current_step', 'count_step', 'progress', 'is_complete')

    def get_count_step(self, lesson):
        return len(Step.objects.filter(lesson=lesson))

    def get_progress(self, lesson):
        profile_lesson_list = ProfileLesson.objects.filter(lesson=lesson, profile=self.context.get('profile'))
        if len(profile_lesson_list) == 0:
            return None
        return {
            'progress': profile_lesson_list[0].progress,
            'max_progress': lesson.max_progress,
        }

    def get_is_complete(self, lesson):
        progress = self.get_progress(lesson=lesson)
        if (progress is not None) and (progress.get('progress') == progress.get('max_progress')):
            return True
        return False

    def get_current_step(self, lesson):
        step_list = Step.objects.filter(lesson=lesson)
        if len(step_list) == 0:
            return None
        logs = ProfileActionsLogs.objects.filter(step__in=step_list)
        if len(logs) == 0:
            return step_list[0].path
        current_step = logs[0]
        last_date = current_step.date_action
        for log in logs:
            if log.date_action > last_date:
                last_date = log.date_action
                current_step = log
        return current_step.path


class ActionLessonSerializer(serializers.ModelSerializer):
    count_step = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ('title', 'image_url', 'max_progress', 'count_step', 'path')

    def get_count_step(self, lesson):
        return len(Step.objects.filter(lesson=lesson))

    def create(self, validated_data):
        return Lesson.objects.create(**validated_data, theme=self.context.get('theme'))

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)

        new_image = validated_data.get('image_url', -1)
        if new_image != -1:
            update_image = Util.get_image(old=instance.image_url, new=new_image,
                                          default=Util.DEFAULT_IMAGES.get('lesson'))
            instance.image_url = Util.get_update_image(old=instance.image_url, new=update_image)

        instance.save()
        return instance


# PAGE STEPS
class ProfileStepSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField(default=False)
    is_complete = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Step
        fields = ('path', 'is_active', 'is_complete')

    def get_is_active(self, step):
        if step == self.context.get('current_step'):
            return True
        return False

    def get_is_complete(self, step):
        profile_step_list = ProfileStep.objects.filter(step=step, profile=self.context.get('profile'))
        if len(profile_step_list) == 0:
            return False
        if profile_step_list[0].status.name == Util.PROFILE_COURSE_STATUS_STUDIED_NAME:
            return True
        return False


class StepSerializer(serializers.ModelSerializer):
    is_complete = serializers.SerializerMethodField(default=False)
    prev = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()

    class Meta:
        model = Step
        fields = ('path', 'title', 'content', 'is_complete', 'prev', 'next')

    def get_is_complete(self, step):
        profile_step_list = ProfileStep.objects.filter(step=step, profile=self.context.get('profile'))
        if len(profile_step_list) == 0:
            return False
        if profile_step_list[0].status.name == Util.PROFILE_COURSE_STATUS_STUDIED_NAME:
            return True
        return False

    def get_link(self):
        link_old = self.context.get('request').build_absolute_uri()
        return "/".join(link_old.split('/')[:-2])

    def get_prev(self, step):
        if step.number == 1:
            return None
        step_prev = Step.objects.get(number=step.number - 1)
        return f"{self.get_link()}/{step_prev.path}"

    def get_next(self, step):
        if step.number == Step.objects.filter(lesson=step.lesson):
            return None
        step_next = Step.objects.get(number=step.number + 1)
        return f"{self.get_link()}/{step_next.path}"


class ActionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ('title', 'content', 'max_progress', 'path')

    @staticmethod
    def update_numbers(step_list):
        for i in range(len(step_list)):
            step_list[i].number = i + 1
            step_list[i].save()

    def create(self, validated_data):
        lesson = self.context.get('lesson')
        number = self.context.get('number')
        step = Step.objects.create(**validated_data, lesson=lesson, number=number)
        MaxProgressUpdater.update_max_progress(old=0, new=1, step=step)
        return step

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)

        new_max_progress = validated_data.get('max_progress', None)
        if (new_max_progress is not None) and (new_max_progress != instance.max_number):
            MaxProgressUpdater.update_max_progress(old=instance.max_progress, new=new_max_progress, step=instance)

        instance.save()
        return instance


# #########################################
#        ######## GRADE ########
# #########################################

class GradeCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileCourse
        fields = ('grade',)

    @staticmethod
    def add_course_star(course, grade):
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
        profile_course = self.context.get('profile_course')
        if profile_course.grade is not None:
            self.difference_course_star(course=profile_course.course, grade=profile_course.grade)
            self.update_rating_course(course=profile_course.course)
            profile_course.grade = None
            profile_course.save()
        return profile_course
