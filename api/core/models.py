import datetime

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class Profile(models.Model):
    """Advanced User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=64)
    avatar_url = models.ImageField(default="profile-default.jpg")
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


# ############## COURSE START ###############
class CourseStatus(models.Model):
    """Status Course: Dev, Release"""
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.name}'


class Course(models.Model):
    """Course"""
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=175, blank=True)
    price = models.IntegerField(default=0)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    avatar_url = models.ImageField(default="course-default.svg")
    duration_in_minutes = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    members_amount = models.IntegerField(default=0)
    max_progress_points = models.IntegerField(default=0)
    status = models.ForeignKey(CourseStatus, blank=True, null=True, on_delete=models.SET_NULL)
    date_create = models.DateField(default=datetime.date.today)
    path = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f'{self.profile.user.username}: {self.title}  [Course]'


def create_course(sender, **kwargs):
    """When a course is created, autofill fields"""
    if kwargs['created']:
        course = kwargs['instance']
        course.path = course.pk
        course_status = CourseStatus.objects.filter(name="В разработке")[0]
        course.status = course_status
        course.save()


post_save.connect(create_course, sender=Course)


# -------------- Page Course START ---------------
class CourseInfo(models.Model):
    """CourseInfo"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title_image_url = models.ImageField(blank=True)
    goal_description = models.TextField()

    def __str__(self):
        return f"{self.course.profile.user.username}: {self.course.title} [Info]"


class CourseFit(models.Model):
    """CourseFit"""
    course_info = models.ForeignKey(CourseInfo, on_delete=models.CASCADE)
    title = models.CharField(max_length=32)
    description = models.TextField(max_length=256)

    def __str__(self):
        return f"{self.course_info.course.profile.user.username}: {self.course_info.course.title}: {self.title} [Fit]"


class CourseStars(models.Model):
    """CourseStars"""
    course_info = models.ForeignKey(CourseInfo, on_delete=models.CASCADE)
    one_stars_count = models.IntegerField(default=0)
    two_stars_count = models.IntegerField(default=0)
    three_stars_count = models.IntegerField(default=0)
    four_stars_count = models.IntegerField(default=0)
    five_stars_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course_info.course.profile.user.username}: {self.course_info.course.title} [Course Stars]"


class CourseSkill(models.Model):
    """CourseSkill"""
    course_info = models.ForeignKey(CourseInfo, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.course_info.course.profile.user.username}: {self.course_info.course.title}: {self.name} [Skill]"


# -------------- Page Course END -----------------


# ------------ Content Course START --------------
class Theme(models.Model):
    """The Course consists of Theme"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    image_url = models.ImageField(blank=True)

    def __str__(self):
        return f"{self.course.profile.user.username}: {self.course.title}: {self.title} [Theme]"


class Lesson(models.Model):
    """The Theme consists of Lesson"""
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    image_url = models.ImageField(blank=True)

    def __str__(self):
        return f"{self.theme.course.profile.user.username}: {self.theme.course.title}: {self.theme.title}: {self.title} [Lesson]"


class Step(models.Model):
    """The Lesson consists of Step"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    content = RichTextUploadingField(blank=True)

    def __str__(self):
        return f"{self.lesson.theme.course.profile.user.username}: {self.lesson.theme.course.title}: {self.lesson.theme.title}: {self.lesson.title}: {self.title} [Step]"


# ------------ Content Course END ----------------

# ------------ Profile to Course START --------------
class ProfileCourseStatus(models.Model):
    """Status Profile to Course: Being studied, Completed"""
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} [Status Profile to Course]"


class ProfileCourse(models.Model):
    """ProfileCourse"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.ForeignKey(ProfileCourseStatus, blank=True, null=True, on_delete=models.SET_NULL)
    progress = models.IntegerField(default=0)
    point = models.IntegerField(blank=True, null=True)
    date_added = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"\"{self.profile.user.username}\" to \"{self.course.title}\""


def create_profile_to_course(sender, **kwargs):
    """When a ProfileCourse is created, autofill fields"""
    if kwargs['created']:
        profile_course = kwargs['instance']
        profile_course_status = ProfileCourseStatus.objects.filter(name="Изучается")[0]
        profile_course.status = profile_course_status
        profile_course.save()


post_save.connect(create_profile_to_course, sender=ProfileCourse)


class ProfileTheme(models.Model):
    """ProfileTheme"""
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"\"{self.profile.user.username}\" to \"{self.theme.course.title}: {self.theme.title}\""


class ProfileLesson(models.Model):
    """ProfileLesson"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"\"{self.profile.user.username}\" to \"{self.lesson.theme.course.title}: {self.lesson.theme.title}: {self.lesson.title}\""


class ProfileStepStatus(models.Model):
    """Status Profile to Step course: Being studied, Completed"""
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} [Status Profile to Step course]"


class ProfileStep(models.Model):
    """ProfileStep"""
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.ForeignKey(ProfileStepStatus, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"\"{self.profile.user.username}\" to \"{self.step.lesson.theme.course.title}: {self.step.lesson.theme.title}: {self.step.lesson.title}: {self.step.title}\""


def create_profile_to_course(sender, **kwargs):
    """When a ProfileStep is created, autofill fields"""
    if kwargs['created']:
        profile_step = kwargs['instance']
        profile_step_status = ProfileStepStatus.objects.filter(name="Изучается")[0]
        profile_step.status = profile_step_status
        profile_step.save()


post_save.connect(create_profile_to_course, sender=ProfileStep)


# -------- Profile to Course END ------------
# ############## COURSE END #################


# ########### COLLECTION START ##############
class Collection(models.Model):
    """Collection"""
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=512, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image_url = models.ImageField(default="collection-default.svg")
    wallpaper = models.ImageField(blank=True)
    rating = models.FloatField(default=0)
    members_amount = models.IntegerField(default=0)
    date_create = models.DateField(default=datetime.date.today)
    path = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f'{self.profile.user.username}: {self.title}  [Collection]'


def create_collection(sender, **kwargs):
    """When a Collection is created, autofill fields"""
    if kwargs['created']:
        collection = kwargs['instance']
        collection.path = collection.pk
        collection.save()


post_save.connect(create_collection, sender=Collection)


class CourseCollection(models.Model):
    """CourseCollection"""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_added = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"\"{self.course.title}\" to \"{self.collection.title}\" [Course to Collection]"


class ProfileCollection(models.Model):
    """ProfileCollection"""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    point = models.IntegerField(blank=True, null=True)
    date_added = models.DateField(default=datetime.date.today, blank=True, null=True)

    def __str__(self):
        return f"\"{self.profile.user.username}\" to \"{self.collection.title}\" [Profile to Collection]"


class CollectionStars(models.Model):
    """CollectionStars"""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    one_stars_count = models.IntegerField(default=0)
    two_stars_count = models.IntegerField(default=0)
    three_stars_count = models.IntegerField(default=0)
    four_stars_count = models.IntegerField(default=0)
    five_stars_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.collection.profile.user.username}: {self.collection.title} [CollectionStars]"

# ############ COLLECTION END ###############
