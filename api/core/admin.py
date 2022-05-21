from django.contrib import admin
from .models import Profile, Subscription, \
    CourseStatus, Course, \
    CourseInfo, CourseFit, CourseStars, CourseSkill, \
    Theme, Lesson, Step, \
    ProfileCourseStatus, ProfileCourse, ProfileTheme, ProfileLesson


# Register your models here.

# PROFILE
admin.site.register(Profile)
admin.site.register(Subscription)

# COURSE
admin.site.register(CourseStatus)
admin.site.register(Course)

# Page COURSE
admin.site.register(CourseInfo)
admin.site.register(CourseFit)
admin.site.register(CourseStars)
admin.site.register(CourseSkill)

# Content COURSE
admin.site.register(Theme)
admin.site.register(Lesson)
admin.site.register(Step)

# Profile to Course START
admin.site.register(ProfileCourseStatus)
admin.site.register(ProfileCourse)
admin.site.register(ProfileTheme)
admin.site.register(ProfileLesson)
