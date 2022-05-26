from rest_framework import serializers

from .models_course import Course, ProfileCourse, Theme, Lesson, \
    Step, ProfileStep, CourseFit, CourseInfo, CourseSkill, CourseStars

from ..collection.models_collection import CourseCollection

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
            return profile_to_course[0].status.name
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
                    max_progress += step.max_mark
                    progress += ProfileStep.objects.get(step=step, profile=profile).mark
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

    @staticmethod
    def get_quantity_in_collection(course):
        return len(CourseCollection.objects.filter(course=course))

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
        fields = ('title', 'description', 'author', 'avatar_url', 'duration_in_minutes', 'rating', 'members_amount',
                  'status_progress', 'progress')

    @staticmethod
    def get_author(collection):
        return collection.profile.user.username

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
    fits = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()

    class Meta:
        model = CourseInfo
        fields = ('title_image_url', 'goal_description', 'fits', 'skills', 'stars')

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
        stars = CourseStars.objects.get(course_info=course_info)
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