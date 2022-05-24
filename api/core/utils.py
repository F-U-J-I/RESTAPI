from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse


class Util:
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

