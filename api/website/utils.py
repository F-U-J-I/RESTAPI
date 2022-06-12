import os

from django.contrib.sites.shortcuts import get_current_site


class Util:
    PROFILE_COURSE_STATUS_SEE_NAME = 'Наблюдающий'
    PROFILE_COURSE_STATUS_STUDIED_NAME = 'Завершен'
    PROFILE_COURSE_STATUS_STUDYING_NAME = 'Изучается'

    PROFILE_COURSE_ROLE_ADMIN_NAME = 'Admin'
    PROFILE_COURSE_ROLE_USER_NAME = 'User'

    COURSE_STATUS_DEV_NAME = 'В разработке'
    COURSE_STATUS_RELEASE_NAME = 'Опубликован'

    DEFAULT_IMAGES = {
        'profile': "!default-profile.jpg",
        'collection': "!default-collection.png",
        'course': "!default-course.png",
        'theme': "!default-theme.png",
        'lesson': "!default-lesson.png",
    }

    PROTOCOL = 'http'

    @staticmethod
    def get_absolute_url(request):
        return f"{Util.PROTOCOL}://{get_current_site(request).domain}"
