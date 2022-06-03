from django.contrib.auth.models import AnonymousUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from .models_profile import Profile, Subscription
from .serializers_profile import ProfileSerializer, MiniProfileSerializer, HeaderProfileSerializer
from ..course.models_course import ProfileCourse, ProfileCourseStatus
from ..course.serializers_course import MiniCourseSerializer
from ..utils import Util, HelperFilter, HelperPaginatorValue, HelperPaginator


class ProfileView(viewsets.ModelViewSet):
    """Profile"""
    lookup_field = 'slug'
    queryset = Profile.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProfileSerializer

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = HelperFilter.PROFILE_FILTER_FIELDS
    search_fields = HelperFilter.PROFILE_SEARCH_FIELDS
    ordering_fields = HelperFilter.PROFILE_ORDERING_FIELDS

    pagination_max_page = HelperPaginatorValue.PROFILE_MAX_PAGE

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    def get_frame_pagination(self, request, queryset, max_page=None):
        if max_page is None:
            max_page = self.pagination_max_page
        pagination = HelperPaginator(request=request, queryset=queryset, max_page=max_page)
        return {
            "count": pagination.get_count(),
            "pages": pagination.get_num_pages(),
            "next": pagination.get_link_next_page(),
            "previous": pagination.get_link_previous_page(),
            "results": pagination.page_obj
        }

    @action(methods=['get'], detail=False)
    def get_list_profile(self, request):
        auth = None
        if type(self.request.user) != AnonymousUser:
            auth = Profile.objects.get(user=self.request.user)

        queryset = self.filter_queryset(self.queryset)
        frame_pagination = self.get_frame_pagination(request, queryset)
        serializer = ProfileSerializer(frame_pagination.get('results'), many=True, context={'auth': auth})
        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_list_mini_profile(self, request):
        queryset = self.filter_queryset(self.queryset)
        frame_pagination = self.get_frame_pagination(request, queryset,
                                                     max_page=HelperPaginatorValue.MINI_PROFILE_MAX_PAGE)
        serializer = MiniProfileSerializer(frame_pagination.get('results'), many=True)
        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_header_profile(self, request, path):
        """Верхняя информация на странице любого пользователя"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = None
        if type(self.request.user) != AnonymousUser:
            auth = Profile.objects.get(user=self.request.user)

        profile = Profile.objects.get(path=path)
        return Response(HeaderProfileSerializer(profile, context={'auth': auth}).data, status=status.HTTP_200_OK)


class CourseProfileView(viewsets.ModelViewSet):
    """Course Profile"""
    lookup_field = 'slug'
    queryset = Profile.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProfileSerializer

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = HelperFilter.COURSE_FILTER_FIELDS
    search_fields = HelperFilter.COURSE_SEARCH_FIELDS
    ordering_fields = HelperFilter.COURSE_ORDERING_FIELDS

    pagination_max_page = HelperPaginatorValue.PROFILE_MAX_PAGE

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    def swap_filters_field(self, type_filter):
        (self.filter_fields, self.search_fields, self.ordering_fields) = HelperFilter.get_filters_course_field(
            type_filter)

    def get_frame_pagination(self, request, queryset, max_page=None):
        if max_page is None:
            max_page = self.pagination_max_page
        pagination = HelperPaginator(request=request, queryset=queryset, max_page=max_page)
        return {
            "count": pagination.get_count(),
            "pages": pagination.get_num_pages(),
            "next": pagination.get_link_next_page(),
            "previous": pagination.get_link_previous_page(),
            "results": pagination.page_obj
        }

    @action(methods=['get'], detail=False)
    def get_studying_courses(self, request, path):
        """Какие курсы ИЗУЧАЕТ студент"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = None
        if type(self.request.user) != AnonymousUser:
            auth = Profile.objects.get(user=self.request.user)
        profile = Profile.objects.get(path=path)

        self.swap_filters_field(HelperFilter.PROFILE_COURSE_TYPE)
        status_studying = ProfileCourseStatus.objects.filter(name=Util.PROFILE_COURSE_STATUS_STUDYING_NAME)
        profile_course_list = ProfileCourse.objects.filter(profile=profile, status__in=status_studying)
        queryset = self.filter_queryset(profile_course_list)
        self.swap_filters_field(HelperFilter.COURSE_TYPE)

        frame_pagination = self.get_frame_pagination(request, queryset,
                                                     max_page=HelperPaginatorValue.MINI_COURSE_MAX_PAGE)
        serializer_list = list()
        for profile_course in frame_pagination.get('results'):
            serializer_list.append(
                MiniCourseSerializer(profile_course.course, context={'profile': profile, 'auth': auth}).data)
        frame_pagination['results'] = serializer_list
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_studied_courses(self, request, path):
        """Какие курсы ИЗУЧИЛ студент"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = None
        if type(self.request.user) != AnonymousUser:
            auth = Profile.objects.get(user=self.request.user)
        profile = Profile.objects.get(path=path)

        self.swap_filters_field(HelperFilter.PROFILE_COURSE_TYPE)
        status_studied = ProfileCourseStatus.objects.filter(name=Util.PROFILE_COURSE_STATUS_STUDIED_NAME)
        profile_course_list = ProfileCourse.objects.filter(profile=profile, status__in=status_studied)
        queryset = self.filter_queryset(profile_course_list)
        self.swap_filters_field(HelperFilter.COURSE_TYPE)

        frame_pagination = self.get_frame_pagination(request, queryset,
                                                     max_page=HelperPaginatorValue.MINI_COURSE_MAX_PAGE)

        serializer_list = list()
        for profile_course in frame_pagination.get('results'):
            serializer_list.append(
                MiniCourseSerializer(profile_course.course, context={'profile': profile, 'auth': auth}).data)
        frame_pagination['results'] = serializer_list
        return Response(frame_pagination, status=status.HTTP_200_OK)

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


class SubscriptionProfileView(viewsets.ModelViewSet):
    """Profile"""
    lookup_field = 'slug'
    profiles = Profile.objects.all()
    queryset = Subscription.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def exists_path(self, path):
        return len(self.profiles.filter(path=path)) != 0

    def is_subscribe(self, goal, subscriber):
        return len(Subscription.objects.filter(goal=goal, subscriber=subscriber)) != 0

    @action(methods=['get'], detail=False)
    def get_goals_subscription_profile(self, request, path):
        """На кого подписан"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = self.profiles.get(path=path)
        auth = self.profiles.get(user=self.request.user)

        goal_list = list()
        for goal_profile in self.queryset.filter(subscriber=profile):
            goal_list.append(ProfileSerializer(goal_profile.goal, context={'auth': auth}).data)
        return Response(goal_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_subscribers_profile(self, request, path):
        """Кто подписан на профиль"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = self.profiles.get(path=path)
        auth = self.profiles.get(user=self.request.user)

        subscriber_list = list()
        for subscriber_profile in self.queryset.filter(goal=profile):
            subscriber_list.append(ProfileSerializer(subscriber_profile.subscriber, context={'auth': auth}).data)
        return Response(subscriber_list, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_goal_subscription(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = self.profiles.get(path=path)
        auth = self.profiles.get(user=self.request.user)
        if profile == auth:
            return Response({'error': 'Вы не можете подписаться или отписаться от себя'},
                            status=status.HTTP_400_BAD_REQUEST)

        if self.is_subscribe(goal=profile, subscriber=auth):
            return Response({'error': 'Вы уже подписались на этого пользователя'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = Subscription.objects.create(goal=profile, subscriber=auth)
        serializer.save()
        return Response({
            'success': f'Успешно подписались на {profile.user.username}'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_goal_subscription(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = self.profiles.get(path=path)
        auth = self.profiles.get(user=self.request.user)
        if profile == auth:
            return Response({'error': 'Вы не можете подписаться или отписаться от себя'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not self.is_subscribe(goal=profile, subscriber=auth):
            return Response({'error': 'Вы уже отписались на этого пользователя'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = Subscription.objects.get(goal=profile, subscriber=auth)
        serializer.delete()
        return Response({
            'success': f'Успешно отписались от {profile.user.username}'
        }, status=status.HTTP_200_OK)
