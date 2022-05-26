from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class Profile(models.Model):
    """Advanced User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=64, unique=True)
    avatar_url = models.ImageField(blank=True, null=True)
    wrapper_url = models.ImageField(blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user}'


def create_profile(sender, **kwargs):
    """When a user is created, a profile is also created"""
    if kwargs['created']:
        profile = Profile.objects.create(user=kwargs['instance'])
        profile.path = profile.pk
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
