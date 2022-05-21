from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime


class Profile(models.Model):
    """Advanced User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_path = models.CharField(max_length=32)
    avatar_url = models.ImageField(default="profile-default.jpg")
    wrapper_url = models.ImageField(blank=True)

    def __str__(self):
        return f'{self.user}'


def create_profile(sender, **kwargs):
    """When a user is created, a profile is also created"""
    if kwargs['created']:
        profile = Profile.objects.create(user=kwargs['instance'])
        profile.user_path = profile.pk
        profile.save()


post_save.connect(create_profile, sender=User)


class Subscription(models.Model):
    """
    goal - the one who subscribed
    subscriber - one who subscribes
    """
    goal = models.ForeignKey(Profile, related_name="goal", on_delete=models.CASCADE)
    subscriber = models.ForeignKey(Profile, related_name="subscriber", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.subscriber.user.username} => {self.goal.user.username}'


class CourseStatus(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.name}'


class Course(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=175, blank=True)
    price = models.IntegerField(blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    avatar_url = models.ImageField(default="course-default.svg")
    duration_in_minutes = models.IntegerField(default=0)
    rating = models.FloatField(default=0.)
    members_amount = models.IntegerField(default=0)
    max_progress_points = models.IntegerField(default=0)
    status = models.ForeignKey(CourseStatus, null=True, on_delete=models.SET_NULL)
    date_create = models.DateField(default=datetime.date.today)
    course_path = models.CharField(max_length=32)


def create_course(sender, **kwargs):
    """When a user is created, a profile is also created"""
    if kwargs['created']:
        course = Course.objects.create(user=kwargs['instance'])
        course.course_path = course.pk
        course.save()


post_save.connect(create_course, sender=Course)
