from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers_profile import ProfileSerializer, MiniProfileSerializer, HeaderProfileSerializer
from .models_profile import Profile, Subscription
from ..course.models_course import ProfileCourse, ProfileCourseStatus
from ..course.serializers_course import MiniCourseSerializer
from ..utils import Util


class ProfileView(viewsets.ModelViewSet):
    """Profile"""
    lookup_field = 'slug'
    queryset = Profile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @action(methods=['get'], detail=False)
    def get_list_profile(self, request):
        serializer_profile_list = list()
        auth = Profile.objects.get(user=self.request.user)
        for profile in self.queryset:
            serializer_profile_list.append(ProfileSerializer(profile, context={'auth': auth}).data)
        return Response(serializer_profile_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_list_mini_profile(self, request):
        serializer_profile_list = list()
        for profile in self.queryset:
            serializer_profile_list.append(MiniProfileSerializer(profile).data)
        return Response(serializer_profile_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_studying_courses(self, request, path):
        """Какие курсы ИЗУЧАЕТ студент"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(path=path)
        status_studying = ProfileCourseStatus.objects.filter(name=Util.PROFILE_COURSE_STATUS_STUDYING_NAME)
        profile_course_list = ProfileCourse.objects.filter(profile=profile, status__in=status_studying)

        serializer_course_list = list()
        for profile_course in profile_course_list:
            serializer_course_list.append(
                MiniCourseSerializer(profile_course.course, context={'profile': profile}).data)
        return Response(serializer_course_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_studied_courses(self, request, path):
        """Какие курсы ИЗУЧИЛ студент"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(path=path)
        status_studied = ProfileCourseStatus.objects.filter(name=Util.PROFILE_COURSE_STATUS_STUDIED_NAME)
        profile_course_list = ProfileCourse.objects.filter(profile=profile, status__in=status_studied)

        serializer_course_list = list()
        for profile_course in profile_course_list:
            serializer_course_list.append(
                MiniCourseSerializer(profile_course.course, context={'profile': profile}).data)
        return Response(serializer_course_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_statistic_study_courses(self, request, path):
        """Статистика по студенту по изученным курсам"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(path=path)
        profile_course_list = ProfileCourse.objects.filter(profile=profile)

        studying_quantity = 0
        studied_quantity = 0
        for profile_course in profile_course_list:
            if profile_course.status is None:
                continue
            if profile_course.status.name == Util.PROFILE_COURSE_STATUS_STUDYING_NAME:
                studying_quantity += 1
            elif profile_course.status.name == Util.PROFILE_COURSE_STATUS_STUDIED_NAME:
                studied_quantity += 1

        percent = 0
        if studied_quantity != 0:
            percent = studied_quantity / (studying_quantity + studied_quantity) * 100

        return Response({
            'studying_quantity': studying_quantity,
            'studied_quantity': studied_quantity,
            'percent': percent,
        }, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_header_profile(self, request, path):
        """Верхняя информация на странице любого пользователя"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(path=path)
        auth = Profile.objects.get(user=self.request.user)
        return Response(HeaderProfileSerializer(profile, context={'auth': auth}).data, status=status.HTTP_200_OK)


class SubscriptionProfileView(viewsets.ModelViewSet):
    """Profile"""
    lookup_field = 'slug'
    profiles = Profile.objects.all()
    queryset = Subscription.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def exists_path(self, path):
        return len(self.profiles.filter(path=path)) != 0

    @action(methods=['get'], detail=False)
    def get_subscribing_profile(self, request, path):
        """На кого подписан"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = self.profiles.get(path=path)
        auth = self.profiles.get(user=self.request.user)

        subscribing_list = list()
        for subscribing_profile in self.queryset.filter(subscriber=profile):
            subscribing_list.append(ProfileSerializer(subscribing_profile.subscriber, context={'auth': auth}).data)
        return Response(subscribing_list, status=status.HTTP_200_OK)
