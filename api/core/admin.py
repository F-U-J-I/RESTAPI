from django.contrib import admin

from .profile.models_profile import Profile, Subscription

from .course.models_course import CourseStatus, Course, CourseInfo, CourseMainInfo, CourseFit, CourseStars, CourseSkill, \
    Theme, Lesson, \
    Step, ProfileCourseStatus, ProfileCourse, ProfileTheme, ProfileLesson, ProfileStepStatus, ProfileStep, \
    ProfileCourseRole, CreatorCollection, ProfileCourseCollection
from .collection.models_collection import Collection, ProfileCollection, CollectionStars

# Register your models here.

# PROFILE
admin.site.register(Profile)
admin.site.register(Subscription)

# COURSE
admin.site.register(CourseStatus)
admin.site.register(CreatorCollection)
admin.site.register(Course)

# Page COURSE
admin.site.register(CourseInfo)
admin.site.register(CourseMainInfo)
admin.site.register(CourseFit)
admin.site.register(CourseStars)
admin.site.register(CourseSkill)

# Content COURSE
admin.site.register(Theme)
admin.site.register(Lesson)
admin.site.register(Step)

# Profile to Course START
admin.site.register(ProfileCourseRole)
admin.site.register(ProfileCourseStatus)
admin.site.register(ProfileCourse)
admin.site.register(ProfileCourseCollection)
admin.site.register(ProfileTheme)
admin.site.register(ProfileLesson)
admin.site.register(ProfileStepStatus)
admin.site.register(ProfileStep)

# COLLECTION
admin.site.register(Collection)
admin.site.register(ProfileCollection)
admin.site.register(CollectionStars)
