from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from .models_profile import Profile, Subscription
from .serializers_profile import ProfileSerializer, MiniProfileSerializer, HeaderProfileSerializer, \
    ActionProfileSerializer, ActionUserSerializer, ActionUserPasswordSerializer
from ..course.models_course import ProfileCourse, ProfileCourseStatus
from ..course.serializers_course import MiniCourseSerializer
from ..utils import Util, HelperFilter, HelperPaginatorValue, HelperPaginator


class ProfileView(viewsets.ModelViewSet):
    """View. Геттеры на модель Profile"""
    lookup_field = 'slug'
    queryset = Profile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = HelperFilter.PROFILE_FILTER_FIELDS
    search_fields = HelperFilter.PROFILE_SEARCH_FIELDS
    ordering_fields = HelperFilter.PROFILE_ORDERING_FIELDS

    pagination_max_page = HelperPaginatorValue.PROFILE_MAX_PAGE

    def exists_path(self, path):
        """Существует ли такой путь к странице"""
        return len(self.queryset.filter(path=path)) != 0

    def get_frame_pagination(self, request, queryset, max_page=None):
        """GET. Вернет форму для пагинации"""
        if max_page is None:
            max_page = self.pagination_max_page
        pagination = HelperPaginator(request=request, queryset=queryset, max_page=max_page)
        return {
            "count": pagination.get_count(),
            "pages": pagination.get_num_pages(),
            "next": pagination.get_link_next_page(),
            "previous": pagination.get_link_previous_page(),
            "current_page": pagination.current_page_num,
            "results": pagination.page_obj
        }

    @action(methods=['get'], detail=False)
    def get_profile_data(self, request):
        """GET. Вернёт страницу профиля"""
        auth = Profile.objects.get(user=self.request.user)
        return Response(ProfileSerializer(auth).data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_list_profile(self, request):
        """GET. Вернёт все профили"""
        auth = Profile.objects.get(user=self.request.user)

        queryset = self.filter_queryset(self.queryset)
        frame_pagination = self.get_frame_pagination(request, queryset)
        serializer = ProfileSerializer(frame_pagination.get('results'), many=True, context={'auth': auth})
        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_list_mini_profile(self, request):
        """GET. Вернёт все профили в мини-формах"""
        queryset = self.filter_queryset(self.queryset)
        frame_pagination = self.get_frame_pagination(request, queryset,
                                                     max_page=HelperPaginatorValue.MINI_PROFILE_MAX_PAGE)
        serializer = MiniProfileSerializer(frame_pagination.get('results'), many=True)
        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_header_profile(self, request, path):
        """GET. Верхняя информация на странице любого пользователя"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = Profile.objects.get(user=self.request.user)
        profile = Profile.objects.get(path=path)
        return Response(HeaderProfileSerializer(profile, context={'auth': auth}).data, status=status.HTTP_200_OK)


class ActionProfileView(viewsets.ModelViewSet):
    """View. Действия над моделью профиля"""
    lookup_field = 'slug'
    queryset = Profile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    @staticmethod
    def get_profile_or_error(path):
        """GET. Вернёт профиль или ошибку"""
        profile_list = Profile.objects.filter(path=path)
        if len(profile_list) == 0:
            error_text = "Такого пользователя не существует"
            return {'error': Response({'error': error_text}, status=status.HTTP_404_NOT_FOUND), }
        return {'profile': profile_list[0]}

    def is_valid(self, request, path):
        """Проверка на валидность"""
        profile_dict = self.get_profile_or_error(path=path)
        if profile_dict.get('error', None) is not None:
            return profile_dict.get('error', None)

        profile = profile_dict.get('profile')
        auth = Profile.objects.get(user=self.request.user)
        if profile != auth:
            error_text = "У вас нет доступа для изменения данных от имени этого пользователя"
            return Response({'error': error_text}, status=status.HTTP_200_OK)
        return {'profile': auth}

    @action(methods=['get'], detail=False)
    def get_info(self, request, path):
        """GET. Вернет информацию по пользователю для обновления"""
        profile_dict = self.get_profile_or_error(path=path)
        if profile_dict.get('error', None) is not None:
            return profile_dict.get('error', None)

        profile = profile_dict.get('profile')
        serializer = ActionProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def update_profile(data, profile):
        """Обновление профиля"""
        serializer_profile = ActionProfileSerializer(data=data, instance=profile)
        serializer_profile.is_valid(raise_exception=True)
        try:
            serializer_profile.save()
        except ValueError as ex:
            return {'error': Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)}
        return {'serializer': serializer_profile.data}

    @staticmethod
    def update_user(data, user):
        """Обновление пользователя"""
        serializer_user = ActionUserSerializer(data=data, instance=user)
        serializer_user.is_valid(raise_exception=True)
        serializer_user.save()
        return serializer_user.data

    @action(methods=['put'], detail=False)
    def update_info(self, request, path):
        """PUT. Обновление информации о пользователе"""
        profile_dict = self.is_valid(request=request, path=path)
        if profile_dict.get('error', None) is not None:
            return profile_dict.get('error', None)
        profile = profile_dict.get('profile')

        result_profile = self.update_profile(data=request.data, profile=profile)
        if result_profile.get('error', None) is not None:
            return result_profile.get('error')
        serializer_profile = result_profile.get('serializer')

        serializer_user = self.update_user(data=request.data, user=profile.user)
        return Response({
            'username': serializer_user.get('username'),
            'email': serializer_user.get('email'),
            'avatar_url': serializer_profile.get('avatar_url'),
            'path': serializer_profile.get('path'),
        }, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=False)
    def update_password(self, request, path):
        """PUT. Обновление пароля"""
        profile_dict = self.is_valid(request=request, path=path)
        if profile_dict.get('error', None) is not None:
            return profile_dict.get('error', None)
        profile = profile_dict.get('profile')

        context = {'new_password': request.data.get('new_password')}
        serializer_user = ActionUserPasswordSerializer(data=request.data, instance=profile.user, context=context)
        serializer_user.is_valid(raise_exception=True)
        serializer_user.save()
        return Response({'message': "password успешно обновлен"}, status=status.HTTP_200_OK)


class CourseProfileView(viewsets.ModelViewSet):
    """View. Связь профиля к курсу"""
    lookup_field = 'slug'
    queryset = Profile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = HelperFilter.COURSE_FILTER_FIELDS
    search_fields = HelperFilter.COURSE_SEARCH_FIELDS
    ordering_fields = HelperFilter.COURSE_ORDERING_FIELDS

    pagination_max_page = HelperPaginatorValue.PROFILE_MAX_PAGE

    def exists_path(self, path):
        """Существует ли такой путь"""
        return len(self.queryset.filter(path=path)) != 0

    def swap_filters_field(self, type_filter):
        """Смена типов фильтрации"""
        (self.filter_fields, self.search_fields, self.ordering_fields) = HelperFilter.get_filters_course_field(
            type_filter)

    def get_frame_pagination(self, request, queryset, max_page=None):
        """Вернет каркас для пагинации"""
        if max_page is None:
            max_page = self.pagination_max_page
        pagination = HelperPaginator(request=request, queryset=queryset, max_page=max_page)
        return {
            "count": pagination.get_count(),
            "pages": pagination.get_num_pages(),
            "next": pagination.get_link_next_page(),
            "previous": pagination.get_link_previous_page(),
            "current_page": pagination.current_page_num,
            "results": pagination.page_obj
        }

    @action(methods=['get'], detail=False)
    def get_studying_courses(self, request, path):
        """GET. Какие курсы ИЗУЧАЕТ студент"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

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
        """GET. Какие курсы ИЗУЧИЛ студент"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

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
        """GET. Статистика по студенту по изученным курсам"""
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
    """VIEW. Подписчики к профилю"""
    lookup_field = 'slug'
    profiles = Profile.objects.all()
    queryset = Subscription.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = HelperFilter.SUBSCRIBER_FILTER_FIELDS
    search_fields = HelperFilter.SUBSCRIBER_SEARCH_FIELDS
    ordering_fields = HelperFilter.SUBSCRIBER_ORDERING_FIELDS

    pagination_max_page = HelperPaginatorValue.PROFILE_MAX_PAGE

    def exists_path(self, path):
        """Существует ли такой путь"""
        return len(self.profiles.filter(path=path)) != 0

    def is_subscribe(self, goal, subscriber):
        """Подписан ли пользователь"""
        return len(Subscription.objects.filter(goal=goal, subscriber=subscriber)) != 0

    def swap_filters_field(self, type_filter):
        """Смена типов фильтраций"""
        (self.filter_fields, self.search_fields, self.ordering_fields) = HelperFilter.get_filters_subscription_field(
            type_filter)

    def get_frame_pagination(self, request, queryset, max_page=None):
        """Вернет каркас для пагинации"""
        if max_page is None:
            max_page = self.pagination_max_page
        pagination = HelperPaginator(request=request, queryset=queryset, max_page=max_page)
        return {
            "count": pagination.get_count(),
            "pages": pagination.get_num_pages(),
            "next": pagination.get_link_next_page(),
            "previous": pagination.get_link_previous_page(),
            "current_page": pagination.current_page_num,
            "results": pagination.page_obj
        }

    @action(methods=['get'], detail=False)
    def get_goals_subscription_profile(self, request, path):
        """GET. На кого подписан"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = Profile.objects.get(user=self.request.user)
        profile = Profile.objects.get(path=path)
        queryset = self.filter_queryset(self.queryset.filter(subscriber=profile))

        frame_pagination = self.get_frame_pagination(request, queryset)
        serializer_list = list()
        for subscription in frame_pagination.get('results'):
            serializer_list.append(ProfileSerializer(subscription.goal, context={'auth': auth}).data)
        frame_pagination['results'] = serializer_list
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_subscribers_profile(self, request, path):
        """GET. Кто подписан на профиль"""
        if not self.exists_path(path):
            return Response({'path': "Пути к такому пользователю не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = Profile.objects.get(user=self.request.user)
        profile = Profile.objects.get(path=path)
        self.swap_filters_field(HelperFilter.GOAL_TYPE)
        queryset = self.filter_queryset(self.queryset.filter(goal=profile))
        self.swap_filters_field(HelperFilter.SUBSCRIBER_TYPE)

        frame_pagination = self.get_frame_pagination(request, queryset)
        serializer_list = list()
        for subscriber in frame_pagination.get('results'):
            serializer_list.append(ProfileSerializer(subscriber.subscriber, context={'auth': auth}).data)
        frame_pagination['results'] = serializer_list
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_goal_subscription(self, request, path):
        """POST. Подписаться на профиль"""
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
        """DELETE. Удалить подписку на профиль"""
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
