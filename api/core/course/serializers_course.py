from rest_framework import serializers

from .models_course import Course, ProfileCourse, Theme, Lesson, \
    Step, ProfileStep, \
    CourseInfo, CourseMainInfo, CourseFit, CourseSkill, CourseStars, ProfileTheme


#####################################
#         ##  COURSE ##
#####################################


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
                        max_progress += step.max_mark
                        progress += profile_step.mark
        return {
            'max_progress': max_progress,
            'progress': progress
        }


class CourseSerializer(serializers.ModelSerializer):
    """курс"""
    author = serializers.SerializerMethodField()
    quantity_in_collection = serializers.SerializerMethodField()

    status_progress = serializers.SerializerMethodField(default=None)
    progress = serializers.SerializerMethodField(default=None)

    class Meta:
        model = Course
        fields = ('title', 'description', 'author', 'avatar_url', 'duration_in_minutes', 'rating', 'members_amount',
                  'quantity_in_collection', 'status_progress', 'progress')

    @staticmethod
    def get_author(course):
        return course.profile.user.username

    def get_quantity_in_collection(self, course):
        return len(ProfileCourse.objects.filter(course=course, profile=self.context.get('profile')))

    def get_status_progress(self, course):
        return HelperCourseSerializer.get_status_progress(course=course, profile=self.context.get('profile'))

    def get_progress(self, course):
        return HelperCourseSerializer.get_progress(course=course, profile=self.context.get('profile'))


class MiniCourseSerializer(serializers.ModelSerializer):
    """Мини курс"""
    author = serializers.SerializerMethodField()
    status_progress = serializers.SerializerMethodField(default=None)
    progress = serializers.SerializerMethodField(default=None)

    class Meta:
        model = Course
        fields = (
            'title', 'description', 'author', 'avatar_url', 'duration_in_minutes', 'rating', 'members_amount',
            'status_progress', 'progress')

    @staticmethod
    def get_author(course):
        return course.profile.user.username

    def get_status_progress(self, course):
        return HelperCourseSerializer.get_status_progress(course=course, profile=self.context.get('profile'))

    def get_progress(self, course):
        return HelperCourseSerializer.get_progress(course=course, profile=self.context.get('profile'))


class PageCourseSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    status_progress = serializers.SerializerMethodField(default=None)

    class Meta:
        model = Course
        fields = ('title', 'author', 'avatar_url', 'duration_in_minutes', 'rating', 'members_amount',
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


#####################################


class ThemeSerializer(serializers.ModelSerializer):
    is_complete = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Theme
        fields = ('title', 'image_url', 'max_progress', 'is_complete')

    def get_is_complete(self, theme):
        profile_theme = ProfileTheme.objects.get(theme=theme, profile=self.context.get('profile'))
        if profile_theme.progress == theme.max_progress:
            return True
        return False


class ActionThemeSerializer(serializers.ModelSerializer):
    count_lesson = serializers.SerializerMethodField()

    class Meta:
        model = Theme
        fields = ('title', 'image_url', 'max_progress', 'count_lesson', 'path')

    def get_count_lesson(self, theme):
        return len(Lesson.objects.filter(theme=theme))

    def create(self, validated_data):
        return Theme.objects.create(**validated_data, course=self.context.get('course'))


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
