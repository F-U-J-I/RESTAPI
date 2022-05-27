import datetime

from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.db.models.signals import post_save

from ..profile.models_profile import Profile


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
    avatar_url = models.ImageField(blank=True, null=True)
    duration_in_minutes = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    members_amount = models.IntegerField(default=0)
    max_progress_points = models.IntegerField(default=0)
    status = models.ForeignKey(CourseStatus, blank=True, null=True, on_delete=models.SET_NULL)
    date_create = models.DateField(default=datetime.date.today)
    path = models.CharField(max_length=64, blank=True, unique=True)

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

        profile_course = ProfileCourse.objects.create(course=course, profile=course.profile)
        profile_course.save()
        profile_course.role = ProfileCourseRole.objects.get(name="Admin")
        profile_course.status = None
        profile_course.save()

        course_info = CourseInfo.objects.create(course=course)
        course_info.save()

        course_stars = CourseStars.objects.create(course=course)
        course_stars.save()


post_save.connect(create_course, sender=Course)


# -------------- Page Course START ---------------
class CourseInfo(models.Model):
    """CourseInfo"""
    course = models.OneToOneField(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course.profile.user.username}: {self.course.title} [Info]"


class CourseMainInfo(models.Model):
    """CourseMainInfo"""
    course_info = models.OneToOneField(CourseInfo, on_delete=models.CASCADE)
    title_image_url = models.ImageField(blank=True, null=True)
    goal_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.course_info.course.profile.user.username}: {self.course_info.course.title} [MainInfo]"


class CourseFit(models.Model):
    """CourseFit"""
    course_info = models.ForeignKey(CourseInfo, on_delete=models.CASCADE)
    title = models.CharField(max_length=32)
    description = models.TextField(max_length=256)

    def __str__(self):
        return f"{self.course_info.course.profile.user.username}: {self.course_info.course.title}: {self.title} [Fit]"


class CourseStars(models.Model):
    """CourseStars"""
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    one_stars_count = models.IntegerField(default=0)
    two_stars_count = models.IntegerField(default=0)
    three_stars_count = models.IntegerField(default=0)
    four_stars_count = models.IntegerField(default=0)
    five_stars_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course.profile.user.username}: {self.course.title} [Course Stars]"


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
    image_url = models.ImageField(blank=True, null=True)

    def __str__(self):
        return f"{self.course.profile.user.username}: {self.course.title}: {self.title} [Theme]"


class Lesson(models.Model):
    """The Theme consists of Lesson"""
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    image_url = models.ImageField(blank=True, null=True)

    def __str__(self):
        return f"{self.theme.course.profile.user.username}: {self.theme.course.title}: {self.theme.title}: {self.title} [Lesson]"


class Step(models.Model):
    """The Lesson consists of Step"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    content = RichTextUploadingField(blank=True)
    max_mark = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.lesson.theme.course.profile.user.username}: {self.lesson.theme.course.title}: {self.lesson.theme.title}: {self.lesson.title}: {self.title} [Step]"


# ------------ Content Course END ----------------

# ------------ Profile to Course START --------------
class ProfileCourseRole(models.Model):
    """Role Profile to Course: Admin, User"""
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} [Role Profile to Course]"


class ProfileCourseStatus(models.Model):
    """Status Profile to Course: Being studied, Completed"""
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} [Status Profile to Course]"


class ProfileCourse(models.Model):
    """ProfileCourse"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    role = models.ForeignKey(ProfileCourseRole, blank=True, null=True, on_delete=models.CASCADE )
    status = models.ForeignKey(ProfileCourseStatus, blank=True, null=True, on_delete=models.SET_NULL)
    progress = models.IntegerField(default=0)
    grade = models.IntegerField(blank=True, null=True)
    date_added = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"\"{self.profile.user.username}\" to \"{self.course.title}\""


def create_profile_to_course(sender, **kwargs):
    """When a ProfileCourse is created, autofill fields"""
    if kwargs['created']:
        profile_course = kwargs['instance']
        profile_course.status = ProfileCourseStatus.objects.get(name="Изучается")
        profile_course.role = ProfileCourseRole.objects.get(name="User")
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
    mark = models.IntegerField(default=0)

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
