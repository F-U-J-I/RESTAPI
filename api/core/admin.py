from django.contrib import admin
from .models import Profile, Subscription, CourseStatus, Course

# Register your models here.

admin.site.register(Profile)
admin.site.register(Subscription)

admin.site.register(CourseStatus)
admin.site.register(Course)
