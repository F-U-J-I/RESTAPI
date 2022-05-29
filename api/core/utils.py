from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse


class Util:
    PROFILE_COURSE_STATUS_SEE_NAME = 'Наблюдающий'
    PROFILE_COURSE_STATUS_STUDIED_NAME = 'Завершен'
    PROFILE_COURSE_STATUS_STUDYING_NAME = 'Изучается'

    PROFILE_COURSE_ROLE_ADMIN_NAME = 'Admin'
    PROFILE_COURSE_ROLE_USER_NAME = 'User'

    COURSE_STATUS_DEV_NAME = 'В разработке'
    COURSE_STATUS_RELEASE_NAME = 'Опубликован'

    PROTOCOL = 'http'

    @staticmethod
    def get_absolute_url(request, token=None, to=None):
        return f"{Util.PROTOCOL}://{get_current_site(request).domain}"

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']],
            from_email=data['from_email'],
        )
        email.send()

    @staticmethod
    def get_absolute_url_token(request, to, user):
        token = RefreshToken.for_user(user).access_token
        relative_link = reverse(to)
        return f"{Util.get_absolute_url(request)}{relative_link}?token={token}"


class HelperFilter:

    def __init__(self, filter_fields, search_fields, ordering_fields):
        pass


