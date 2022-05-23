from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from . import serializers
from .models import Profile
from .utils import Util


# Create your views here.
class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        email_body = f"Здравствуйте, {user.username}!\n" \
                     f"Спасибо, что зарегистрировались на нашей платформе!\n" \
                     f"Теперь вы примкнули к кузне, где каждый Кузнец, который стремится стать мастером жадно поглощает " \
                     f"курсы, постигая всё то, что до нас сделали другие...\n\n" \
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
            'user': serializers.UserSerializer(user, context=self.get_serializer_context()).data,
            'message': "Пользователь успешно создан"
        })


class VerifyEmail(generics.GenericAPIView):
    def get(self):
        pass


class ProfileView(generics.GenericAPIView):
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ProfileSerializer

    def get(self, request, path):
        profile = Profile.objects.get(path=path)
        return Response({
            'profile': serializers.ProfileSerializer(profile, context=self.get_serializer_context()).data,
            'user': serializers.UserSerializer(profile.user, context=self.get_serializer_context()).data,
        })


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.ResetPasswordSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data['email'])
        except Exception:
            user = None

        if user:
            token = RefreshToken.for_user(user=user)

            relative_link = reverse('email-verify')
            absolute_url = f"{Util.get_absolute_url(request)}{relative_link}?token={token}"

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

# class CourseViewSet(viewsets.ModelViewSet):
#     lookup_field = 'slug'
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     permission_classes = [permissions.AllowAny]
#     pagination_class = PageNumberSetPagination
#
#     def get_serializer_class(self):
#         if self.action == 'list':
#             return CourseSerializer
#         elif self.action == 'retrieve':
#             return CourseInfoSerializer
#
#     def retrieve(self, request, pk=None, *args, **kwargs):
#         course = Course.objects.get(pk=pk)
#         serializer = CourseSerializer(course)
#         course_info = serializer.get_info(course.pk)
#         modules = Module.objects.filter(course_id=course.pk)
#         module_serializer = ModuleWholeSerializer(modules, many=True)
#         return Response({
#             "course": serializer.data,
#             "info": course_info,
#             "module": module_serializer.data,
#         })
