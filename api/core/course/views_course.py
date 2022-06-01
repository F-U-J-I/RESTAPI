from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from .models_course import Course, CourseInfo, ProfileCourse, CourseStatus, ProfileCourseCollection, Theme
from .serializers_course import GradeCourseSerializer, PageCourseSerializer, PageInfoCourseSerializer, CourseSerializer, \
    MiniCourseSerializer, ActionThemeSerializer
from ..collection.models_collection import Collection
from ..profile.models_profile import Profile
from ..utils import Util, HelperFilter, HelperPaginator, HelperPaginatorValue


class CourseView(viewsets.ModelViewSet):
    """Курсы"""
    lookup_field = 'slug'
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = HelperFilter.COURSE_FILTER_FIELDS
    search_fields = HelperFilter.COURSE_SEARCH_FIELDS
    ordering_fields = HelperFilter.COURSE_ORDERING_FIELDS

    pagination_max_page = HelperPaginatorValue.COURSE_MAX_PAGE

    @staticmethod
    def exists_access_page(course, profile):
        status_development = CourseStatus.objects.get(name=Util.COURSE_STATUS_DEV_NAME)
        status_released = CourseStatus.objects.get(name=Util.COURSE_STATUS_RELEASE_NAME)
        if (course.status == status_released) or (course.status == status_development and profile == course.profile):
            return True
        return False

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @staticmethod
    def exists_profile_path(path):
        return len(Profile.objects.filter(path=path)) != 0

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

    def swap_filters_field(self, type_filter):
        (self.filter_fields, self.search_fields, self.ordering_fields) = HelperFilter.get_filters_course_field(
            type_filter)

    @action(methods=['get'], detail=False)
    def get_courses(self, request, *args, **kwargs):
        auth = Profile.objects.get(user=self.request.user)
        queryset = self.filter_queryset(self.queryset)
        frame_pagination = self.get_frame_pagination(request, queryset)
        serializer = CourseSerializer(frame_pagination.get('results'), many=True, context={'profile': auth})

        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_mini_courses(self, request, *args, **kwargs):
        auth = Profile.objects.get(user=self.request.user)
        queryset = self.filter_queryset(self.queryset)
        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COURSE_PAGE)
        serializer = MiniCourseSerializer(frame_pagination.get('results'), many=True, context={'profile': auth})

        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_all_profile_courses(self, request, path, *args, **kwargs):
        """Добавленные и созданные курсы пользователем по path"""
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(path=path)
        auth = Profile.objects.get(user=self.request.user)

        # Получаем созданные и добавленные курсы
        added_profile_course = ProfileCourse.objects.filter(profile=profile)
        created_queryset = self.queryset.filter(profile=profile)
        queryset_list = [item.course.pk for item in added_profile_course]
        for item in created_queryset:
            queryset_list.append(item.pk)
        new_queryset = self.queryset.filter(pk__in=queryset_list)

        queryset = self.filter_queryset(new_queryset)

        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COURSE_PAGE)
        serializer = MiniCourseSerializer(frame_pagination.get('results'), many=True, context={'profile': auth})
        frame_pagination['results'] = serializer.data

        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_added_courses(self, request, path, *args, **kwargs):
        """Добавленные курсы пользователем по path"""
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(path=path)
        auth = Profile.objects.get(user=self.request.user)

        self.swap_filters_field(HelperFilter.PROFILE_COURSE_TYPE)
        profile_queryset = self.filter_queryset(ProfileCourse.objects.filter(profile=profile))
        self.swap_filters_field(HelperFilter.COURSE_TYPE)

        queryset = [item.course for item in profile_queryset]
        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COURSE_PAGE)
        serializer = MiniCourseSerializer(frame_pagination.get('results'), many=True,
                                          context={'profile': auth})

        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_created_courses(self, request, path, *args, **kwargs):
        """Созданные курсы пользователем по path"""
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(path=path)
        auth = Profile.objects.get(user=self.request.user)

        queryset = self.filter_queryset(self.queryset.filter(profile=profile))
        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COURSE_PAGE)
        serializer = MiniCourseSerializer(frame_pagination.get('results'), many=True, context={'profile': auth})
        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def get_page_course(self, request, path, *args, **kwargs):
        """Страница с информацией о курсе"""
        if not self.exists_path(path):
            return Response({'error': "Такого курса не существует"}, status=status.HTTP_404_NOT_FOUND)

        course = self.queryset.get(path=path)
        profile = Profile.objects.get(user=request.user)
        if not self.exists_access_page(course=course, profile=profile):
            return Response({'error': "У вас нет доступа к этой странице"}, status=status.HTTP_404_NOT_FOUND)

        serializer_course = PageCourseSerializer(course, context={'profile': profile})
        course_info = CourseInfo.objects.get(course=course)
        serializer_course_info = PageInfoCourseSerializer(course_info, context={'profile': profile})
        return Response(data={
            'course': serializer_course.data,
            'info': serializer_course_info.data
        }, status=status.HTTP_200_OK)


# #########################################
#        ######## ACTIONS ########
# #########################################

class ActionCourseView(viewsets.ModelViewSet):
    """Коллекция"""
    lookup_field = 'slug'
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @action(detail=False, methods=['post'])
    def create_course(self, request):
        course_title = request.data.get('title', None)
        if course_title is None:
            return Response({
                'error': "Вы не ввели название курса",
            }, status=status.HTTP_400_BAD_REQUEST)

        auth = Profile.objects.get(user=self.request.user)
        course = Course.objects.create(title=course_title, profile=auth)
        course.save()
        return Response({
            'title': course.title,
            'path': course.path,
            'message': "Курс успешно создан",
        }, status=status.HTTP_200_OK)


class ThemeView(viewsets.ModelViewSet):
    """Тема"""
    lookup_field = 'slug'
    queryset = Theme.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_theme(self, course, path):
        return len(self.queryset.filter(course=course, path=path)) != 0

    @staticmethod
    def exists_course_path(path):
        return len(Course.objects.filter(path=path)) != 0

    @action(detail=False, methods=['post'])
    def create_theme(self, request, path):
        if not self.exists_course_path(path=path):
            return Response({'error': "Такого курса не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = Profile.objects.get(user=self.request.user)
        course = Course.objects.get(path=path)
        if course.profile != auth:
            return Response({"error": "У вас нет доступа для создания темы от имени этого аккаунта"},
                            status=status.HTTP_400_BAD_REQUEST)

        number_new_theme = len(self.queryset.filter(course=course)) + 1
        serializer = ActionThemeSerializer(data={'title': f"Тема #{number_new_theme}"},
                                           context={'profile': auth, 'course': course})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'title': serializer.data['title'],
            'path': serializer.data['path'],
            'message': "Тема успешно создана"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_theme(self, request, path_course, path_theme):
        if not self.exists_course_path(path=path_course):
            return Response({'error': "Такого курса не существует"}, status=status.HTTP_404_NOT_FOUND)

        course = Course.objects.get(path=path_course)
        auth = Profile.objects.get(user=self.request.user)
        if course.profile != auth:
            return Response({"error": "У вас нет доступа для удаления темы от имени этого аккаунта"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not self.exists_theme(course=course, path=path_theme):
            return Response({'error': "Такой темы не существует"}, status=status.HTTP_404_NOT_FOUND)

        theme = self.queryset.get(course=course, path=path_theme)
        theme.delete()
        return Response({
            'title': theme.title,
            'path': theme.path,
            'message': "Тема успешно удалена"
        }, status=status.HTTP_200_OK)


# #########################################
#    ######## ACTIONS PROFILE ########
# #########################################

class ActionProfileCourseView(viewsets.ModelViewSet):
    """Коллекция"""
    lookup_field = 'slug'
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_course(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @staticmethod
    def exists_collection(path):
        return len(Collection.objects.filter(path=path)) != 0

    def get_course(self, path):
        course_list = self.queryset.filter(path=path)
        if len(course_list) == 0:
            raise Http404("Такого курса не существует")
        return course_list[0]

    @action(detail=False, methods=['post'])
    def added_courses(self, request, path):
        collection_path = request.data.get('collection_path')
        if self.exists_course(path=path):
            return Response({'error': "Такого курса не существует"}, status=status.HTTP_404_NOT_FOUND)
        if self.exists_collection(path=collection_path):
            return Response({'error': "Такой подборки не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = Profile.objects.get(user=self.request.user)
        course = Course.objects.get(path=path)
        collection = Collection.objects.get(path=collection_path)
        if collection.profile != auth:
            return Response({
                'error': f"Вы не являетесь создателем подборки, поэтому не имеете право её изменять"
            }, status=status.HTTP_400_BAD_REQUEST)

        profile_course_collection_list = ProfileCourseCollection.objects.filter(profile=auth, course=course,
                                                                                collection=collection)
        if len(profile_course_collection_list) != 0:
            return Response({'error': "Вы уже добавили этот курс"}, status=status.HTTP_404_NOT_FOUND)

        profile_course = ProfileCourse.objects.create(profile=auth, course=course)
        profile_course.save()

        profile_course_collection = ProfileCourseCollection.objects.create(profile=auth, course=course,
                                                                           collection=collection)
        profile_course_collection.save()

        return Response({
            'course': course.title,
            'message': "Курс добавлен в подборку"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def popped_courses(self, request, path):
        auth = Profile.objects.get(user=self.request.user)
        course = self.get_course(path=path)
        collection = self.get_collection(path=request.data.get('collection'))
        if collection.profile != auth:
            return Response({
                'error': f"Вы не являетесь создателем подборки, поэтому не имеете право её изменять"
            }, status=status.HTTP_400_BAD_REQUEST)

        profile_course_collection_list = ProfileCourseCollection.objects.filter(profile=auth, course=course,
                                                                                collection=collection)
        if len(profile_course_collection_list) != 0:
            return Response({'error': "Вы уже удалили этот курс"}, status=status.HTTP_404_NOT_FOUND)

        profile_course_collection = profile_course_collection_list[0]
        profile_course_collection.delete()

        return Response({
            'course': course.title,
            'message': "Курс удален из подборки"
        }, status=status.HTTP_200_OK)


# #########################################
#        ######## GRADE ########
# #########################################

class GradeCourseView(viewsets.ModelViewSet):
    """Курсы"""
    lookup_field = 'slug'
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @action(detail=False, methods=['post'])
    def set_grade(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Такого курса не существует"}, status=status.HTTP_404_NOT_FOUND)

        course = self.queryset.get(path=path)
        profile = Profile.objects.get(user=self.request.user)
        serializer = GradeCourseSerializer(data=request.data, context={'profile': profile, 'course': course})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'course': course.title,
            'path': course.path,
            'grade': serializer.data['grade']
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_grade(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Такого курса не существует"}, status=status.HTTP_404_NOT_FOUND)

        course = self.queryset.get(path=path)
        profile = Profile.objects.get(user=self.request.user)
        profile_course = ProfileCourse.objects.get(profile=profile, course=course)

        serializer = GradeCourseSerializer(data=request.data, instance=profile_course)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'course': course.title,
            'path': course.path,
            'grade': serializer.data['grade']
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_grade(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Такого курса не существует"}, status=status.HTTP_404_NOT_FOUND)

        course = self.queryset.get(path=path)
        profile = Profile.objects.get(user=self.request.user)

        if course.profile != profile:
            return Response({"error": "У вас нет доступа для удаления оценки курса от имени этого аккаунта"},
                            status=status.HTTP_400_BAD_REQUEST)

        profile_course = ProfileCourse.objects.get(profile=profile, course=course)
        serializer = GradeCourseSerializer(context={'profile_course': profile_course})
        serializer.delete_grade()

        return Response({
            'course': course.title,
            'path': course.path,
            'grade': serializer.data['grade']
        }, status=status.HTTP_200_OK)
