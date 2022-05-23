from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage


class Util:
    PROTOCOL = 'http'

    @staticmethod
    def get_absolute_url(request):
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
