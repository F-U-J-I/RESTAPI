import datetime

from django.core.validators import validate_image_file_extension
from django.db import models
from django.db.models.signals import post_save


# ########### COLLECTION START ##############
from ..profile.models_profile import Profile


class Collection(models.Model):
    """Collection"""
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=512, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image_url = models.ImageField(validators=[validate_image_file_extension], blank=True, null=True)
    wallpaper = models.ImageField(blank=True, null=True)
    rating = models.FloatField(default=0)
    members_amount = models.IntegerField(default=0)
    date_create = models.DateField(default=datetime.date.today)
    path = models.CharField(max_length=64, blank=True, unique=True)

    def __str__(self):
        return f'{self.profile.user.username}: {self.title}  [Collection]'


def create_collection(sender, **kwargs):
    """When a Collection is created, autofill fields"""
    if kwargs['created']:
        collection = kwargs['instance']
        collection.path = collection.pk
        collection.save()

        profile_collection = ProfileCollection.objects.create(collection=collection, profile=collection.profile)
        profile_collection.save()

        collection_stars = CollectionStars.objects.create(collection=collection)
        collection_stars.save()


post_save.connect(create_collection, sender=Collection)


class ProfileCollection(models.Model):
    """ProfileCollection"""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    grade = models.IntegerField(blank=True, null=True)
    date_added = models.DateField(default=datetime.date.today, blank=True, null=True)

    def __str__(self):
        return f"\"{self.profile.user.username}\" to \"{self.collection.title}\" [Profile to Collection]"


class CollectionStars(models.Model):
    """CollectionStars"""
    collection = models.OneToOneField(Collection, on_delete=models.CASCADE)
    one_stars_count = models.IntegerField(default=0)
    two_stars_count = models.IntegerField(default=0)
    three_stars_count = models.IntegerField(default=0)
    four_stars_count = models.IntegerField(default=0)
    five_stars_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.collection.profile.user.username}: {self.collection.title} [CollectionStars]"

# ############ COLLECTION END ###############
