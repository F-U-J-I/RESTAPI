from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from .models_course import Course, CourseInfo, ProfileCourse, CourseStatus, ProfileCourseCollection, Theme, Lesson, Step
from .serializers_course import GradeCourseSerializer, PageCourseSerializer, PageInfoCourseSerializer, CourseSerializer, \
    MiniCourseSerializer, ActionThemeSerializer, ActionLessonSerializer, ActionStepSerializer, ProfileThemeSerializer, \
    CourseTitleSerializer, ThemeTitleSerializer, ProfileLessonSerializer, LessonTitleSerializer, ProfileStepSerializer
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


class CourseCompletionPage(viewsets.ModelViewSet):
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]

    # PAGE THEMES
    @action(detail=False, methods=['get'])
    def get_title_course(self, request, path_course):
        exists = ExistsPath.exists(path_course=path_course)
        if exists.get('error', None) is not None:
            return exists.get('error')

        course = Course.objects.get(path=path_course)
        serializer = CourseTitleSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_themes(self, request, path_course):
        exists = ExistsPath.exists(path_course=path_course)
        if exists.get('error', None) is not None:
            return exists.get('error')

        auth = Profile.objects.get(user=self.request.user)
        course = Course.objects.get(path=path_course)
        theme_list = Theme.objects.filter(course=course)
        serializer = ProfileThemeSerializer(theme_list, many=True, context={'profile': auth})

        return Response(serializer.data, status=status.HTTP_200_OK)

    # ###########

    # PAGE LESSONS
    @action(detail=False, methods=['get'])
    def get_title_theme(self, request, path_course, path_theme):
        exists = ExistsPath.exists(path_course=path_course, path_theme=path_theme)
        if exists.get('error', None) is not None:
            return exists.get('error')

        theme = Theme.objects.get(path=path_theme)
        serializer = ThemeTitleSerializer(theme)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_lessons(self, request, path_course, path_theme):
        exists = ExistsPath.exists(path_course=path_course, path_theme=path_theme)
        if exists.get('error', None) is not None:
            return exists.get('error')

        auth = Profile.objects.get(user=self.request.user)
        theme = Theme.objects.get(path=path_theme)
        lesson_list = Lesson.objects.filter(theme=theme)
        serializer = ProfileLessonSerializer(lesson_list, many=True, context={'profile': auth})

        return Response(serializer.data, status=status.HTTP_200_OK)

    # ###########

    # PAGE STEPS
    @action(detail=False, methods=['get'])
    def get_steps(self, request, path_course, path_theme, path_lesson, path_step):
        exists = ExistsPath.exists(path_course=path_course, path_theme=path_theme, path_lesson=path_lesson,
                                   path_step=path_step)
        if exists.get('error', None) is not None:
            return exists.get('error')

        auth = Profile.objects.get(user=self.request.user)
        lesson = Lesson.objects.get(path=path_lesson)
        step_list = Step.objects.filter(lesson=lesson)
        current_step = step_list.get(path=path_step)
        serializer = ProfileStepSerializer(step_list, many=True,
                                           context={'profile': auth, 'current_step': current_step})

        return Response(serializer.data, status=status.HTTP_200_OK)
    # ###########


class ThemeView(viewsets.ModelViewSet):
    """Тема"""
    lookup_field = 'slug'
    queryset = Theme.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_theme(self, request, path):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        course = Course.objects.get(path=path)
        number_new_theme = len(self.queryset.filter(course=course)) + 1
        serializer = ActionThemeSerializer(data={'title': f"Тема #{number_new_theme}"}, context={'course': course})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'title': serializer.data['title'],
            'path': serializer.data['path'],
            'message': "Тема успешно создана"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_update_info(self, request, path_course, path_theme):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        course = Course.objects.get(path=path_course)
        theme = self.queryset.get(path=path_theme)
        serializer = ActionThemeSerializer(theme, context={'course': course})

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_theme(self, request, path_course, path_theme):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        course = Course.objects.get(path=path_course)
        theme = self.queryset.get(path=path_theme)
        serializer = ActionThemeSerializer(data=request.data, instance=theme, context={'course': course})
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except ValueError as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_theme(self, request, path_course, path_theme):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        theme = self.queryset.get(path=path_theme)
        theme.delete()
        return Response({
            'title': theme.title,
            'path': theme.path,
            'message': "Тема успешно удалена"
        }, status=status.HTTP_200_OK)


class LessonView(viewsets.ModelViewSet):
    """Тема"""
    lookup_field = 'slug'
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_lesson(self, request, path_course, path_theme):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        theme = Theme.objects.get(path=path_theme)
        number_new_lesson = len(self.queryset.filter(theme=theme)) + 1
        path_lesson = Util.get_max_path(self.queryset.filter(theme=theme)) + 1
        serializer = ActionLessonSerializer(data={'title': f"Урок #{number_new_lesson}", 'path': path_lesson},
                                            context={'theme': theme})
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except ValueError as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'title': serializer.data['title'],
            'path': serializer.data['path'],
            'message': "Урок успешно создан"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_update_info(self, request, path_course, path_theme, path_lesson):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme,
                                       path_lesson=path_lesson)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        theme = Theme.objects.get(path=path_theme)
        lesson = self.queryset.get(path=path_lesson)
        serializer = ActionLessonSerializer(lesson, context={'theme': theme})

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_lesson(self, request, path_course, path_theme, path_lesson):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        theme = Theme.objects.get(path=path_theme)
        lesson = self.queryset.get(path=path_lesson)
        serializer = ActionLessonSerializer(data=request.data, instance=lesson, context={'theme': theme})
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except ValueError as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_lesson(self, request, path_course, path_theme, path_lesson):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        lesson = self.queryset.get(path=path_lesson)
        lesson.delete()
        return Response({
            'title': lesson.title,
            'path': lesson.path,
            'message': "Урок успешно удален"
        }, status=status.HTTP_200_OK)


class StepView(viewsets.ModelViewSet):
    """Шаг"""
    lookup_field = 'slug'
    queryset = Step.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_step(self, request, path_course, path_theme, path_lesson):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme,
                                       path_lesson=path_lesson)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        lesson = Lesson.objects.get(path=path_lesson)
        number_new_step = len(self.queryset.filter(lesson=lesson)) + 1
        path_step = Util.get_max_path(self.queryset.filter(lesson=lesson)) + 1
        serializer = ActionStepSerializer(data={'title': f"Шаг #{number_new_step}", 'path': path_step},
                                          context={'lesson': lesson})
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except ValueError as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'title': serializer.data['title'],
            'path': serializer.data['path'],
            'message': "Шаг успешно создан"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_update_info(self, request, path_course, path_theme, path_lesson, path_step):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme,
                                       path_lesson=path_lesson, path_step=path_step)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        lesson = Lesson.objects.get(path=path_lesson)
        step = self.queryset.get(path=path_step)
        serializer = ActionStepSerializer(step, context={'lesson': lesson})

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_step(self, request, path_course, path_theme, path_lesson, path_step):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme,
                                       path_lesson=path_lesson, path_step=path_step)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        step = self.queryset.get(path=path_step)
        serializer = ActionStepSerializer(data=request.data, instance=step, context={'step': step})
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except ValueError as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_step(self, request, path_course, path_theme, path_lesson, path_step):
        is_valid = ExistsPath.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme,
                                       path_lesson=path_lesson, path_step=path_step)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        step = self.queryset.get(path=path_step)
        print(step.delete())
        return Response({
            'title': step.title,
            'path': step.path,
            'message': "Шаг успешно удален"
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


class ExistsPath:

    @staticmethod
    def get_exists(path, model, error_text):
        if path is not None:
            if not Util.exists_path(model, {'path': path}):
                return {
                    'valid': False,
                    'error': Response({'error': error_text}, status=status.HTTP_404_NOT_FOUND),
                }
        return {'valid': True}

    @staticmethod
    def is_valid(user=None, path_course=None, path_theme=None, path_lesson=None, path_step=None):
        if user is not None:
            is_access = ExistsPath.is_access(user=user, path_course=path_course)
            if is_access.get('error', None) is not None:
                return is_access

        exists = ExistsPath.exists(path_course=path_course, path_theme=path_theme, path_lesson=path_lesson,
                                   path_step=path_step)
        if exists.get('error', None) is not None:
            return exists
        return {'valid': True}

    @staticmethod
    def exists(path_course=None, path_theme=None, path_lesson=None, path_step=None):
        if path_course is not None:
            exists_course = ExistsPath.exists_course(path_course=path_course)
            if exists_course.get('error', None) is not None:
                return exists_course

        exists_theme = ExistsPath.exists_theme(path_theme=path_theme)
        if exists_theme.get('error', None) is not None:
            return exists_theme

        exists_lesson = ExistsPath.exists_lesson(path_lesson=path_lesson)
        if exists_lesson.get('error', None) is not None:
            return exists_lesson

        exists_step = ExistsPath.exists_step(path_step=path_step)
        if exists_step.get('error', None) is not None:
            return exists_step
        return {'valid': True}

    @staticmethod
    def exists_course(path_course):
        return ExistsPath.get_exists(path=path_course, model=Course, error_text="Такого курса не существует")

    @staticmethod
    def exists_theme(path_theme):
        return ExistsPath.get_exists(path=path_theme, model=Theme, error_text="Такой темы не существует")

    @staticmethod
    def exists_lesson(path_lesson):
        return ExistsPath.get_exists(path=path_lesson, model=Lesson, error_text="Такого урока не существует")

    @staticmethod
    def exists_step(path_step):
        return ExistsPath.get_exists(path=path_step, model=Step, error_text="Такого шага не существует")

    @staticmethod
    def is_access(user, path_course):
        auth = Profile.objects.get(user=user)
        course = Course.objects.get(path=path_course)
        if course.profile != auth:
            error_text = "У вас нет доступа для создания/изменения/удаления шага от имени этого аккаунта"
            return {
                'valid': False,
                'error': Response({'error': error_text}, status=status.HTTP_404_NOT_FOUND),
            }
        return {'valid': False}
