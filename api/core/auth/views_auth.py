import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import permissions, generics, status
from rest_framework.response import Response

from .serializers_auth import RegisterSerializer, RequestPasswordResetEmailSerializer, SetNewPasswordSerializer
from ..profile.serializers_profile import UserSerializer
from ..profile.models_profile import Profile
from ..utils import Util


# Create your views here.
class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        absolute_url = Util.get_absolute_url_token(request, to='email-verify', user=user)

        email_body = f"Здравствуйте, {user.username}!\n" \
                     f"Спасибо, что зарегистрировались на нашей платформе!\n" \
                     f"Теперь вы примкнули к кузне, где каждый Кузнец, который стремится стать мастером жадно поглощает " \
                     f"курсы, постигая всё то, что до нас сделали другие...\n\n" \
                     f"Для подтверждения аккаунта перейдите по этой ссылке: {absolute_url}\n\n" \
                     f"--\n" \
                     f"С уважением, от \"FUJI\""

        data = {
            'email_subject': 'Успешная регистрация',
            'email_body': email_body,
            'to_email': user.email,
            'from_email': 'teamfuji@yandex.ru',
        }

        Util.send_email(data)

        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'message': "Пользователь успешно создан"
        }, status=status.HTTP_200_OK)


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            profile = Profile.objects.get(user=payload['user_id'])
            if not profile.is_verified:
                profile.is_verified = True
                profile.save()
                return Response({'email': "Аккаунт успешно активирован"}, status=status.HTTP_200_OK)
            return Response({'email': "Ваш аккаунт уже активирован"}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as ex:
            return Response({'error': "Не удалось активировать аккаунт"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as ex:
            return Response({'error': "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetEmailView(generics.GenericAPIView):
    """
    Восстановление пароля по Email.
    Сверяет наличие такого email'a и отправляет на него закодированную
    ссылку на восстановление аккаунта
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RequestPasswordResetEmailSerializer

    def post(self, request):
        attrs = request.data
        email = attrs.get('email', '')
        users = User.objects.filter(email=email)
        if users.exists():
            user = users[0]
            uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))

            token = PasswordResetTokenGenerator().make_token(user)
            relative_link = reverse('password-reset-confirm', kwargs={
                'uidb64': uidb64,
                'token': token
            })
            absolute_url = f"{Util.get_absolute_url(request)}{relative_link}"

            email_body = f"Здравствуйте {user.username}!\n" \
                         f"Для восстановления пароля перейдите по этой ссылке: {absolute_url}\n" \
                         f"Если это были не вы, то проигнорируйте данное письмо\n\n" \
                         f"--\n" \
                         f"С уважением, от \"FUJI\""

            data = {
                'email_subject': 'Сброс пароля',
                'email_body': email_body,
                'to_email': user.email,
                'from_email': 'teamfuji@yandex.ru',
            }

            Util.send_email(data)

        return Response({
            'message': 'Мы отправили вам на почту ссылку для сброса пароля',
        },
            status=status.HTTP_200_OK,
        )


class PasswordTokenCheckAPI(generics.GenericAPIView):
    """Декодирование ссылки"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            user_pk = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_pk)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return self.request_error()

            return Response({
                'message': 'Token is valid',
                'uidb64': uidb64,
                'token': token,
            },
                status=status.HTTP_200_OK,
            )

        except DjangoUnicodeDecodeError as ex:
            print(ex)
            return self.request_error()

    @staticmethod
    def request_error():
        return Response({
            'message': 'Token is not valid, please request a new one',
        },
            status=status.HTTP_400_BAD_REQUEST
        )


class SetNewPasswordAPIView(generics.GenericAPIView):
    """Создание нового пароля"""
    permission_classes = [permissions.AllowAny]
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            'message': 'Password reset success',
        },
            status=status.HTTP_200_OK,
        )
