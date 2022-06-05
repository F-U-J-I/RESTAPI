from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from .models_course import Course, CourseInfo, ProfileCourse, CourseStatus, ProfileCourseCollection, Theme, Lesson, \
    Step, ProfileCourseStatus, CourseFit, CourseSkill, CourseMainInfo, ProfileActionsLogs, ProfileStep, \
    ProfileStepStatus
from .serializers_course import GradeCourseSerializer, PageCourseSerializer, PageInfoCourseSerializer, CourseSerializer, \
    MiniCourseSerializer, ActionThemeSerializer, ActionLessonSerializer, ActionStepSerializer, ProfileThemeSerializer, \
    CourseTitleSerializer, ThemeTitleSerializer, ProfileLessonSerializer, GetStepSerializer, StepSerializer, \
    MaxProgressUpdater, CourseFitSerializer, CourseSkillSerializer, EditPageInfoCourseSerializer, ProfileStepSerializer
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
        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COURSE_MAX_PAGE)
        serializer = MiniCourseSerializer(frame_pagination.get('results'), many=True, context={'profile': auth})

        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_all_profile_courses(self, request, path, *args, **kwargs):
        """Добавленные и созданные курсы пользователем по path"""
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = Profile.objects.get(user=self.request.user)

        # Получаем созданные и добавленные курсы
        profile = Profile.objects.get(path=path)
        added_profile_course = ProfileCourse.objects.filter(profile=profile)
        created_queryset = self.queryset.filter(profile=profile)
        queryset_list = [item.course.pk for item in added_profile_course]
        for item in created_queryset:
            queryset_list.append(item.pk)
        new_queryset = self.queryset.filter(pk__in=queryset_list)

        queryset = self.filter_queryset(new_queryset)

        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COURSE_MAX_PAGE)
        serializer = MiniCourseSerializer(frame_pagination.get('results'), many=True, context={'profile': auth})
        frame_pagination['results'] = serializer.data

        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_added_courses(self, request, path, *args, **kwargs):
        """Добавленные курсы пользователем по path"""
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = Profile.objects.get(user=self.request.user)

        profile = Profile.objects.get(path=path)
        self.swap_filters_field(HelperFilter.PROFILE_COURSE_TYPE)
        profile_queryset = self.filter_queryset(ProfileCourse.objects.filter(profile=profile))
        self.swap_filters_field(HelperFilter.COURSE_TYPE)

        queryset = [item.course for item in profile_queryset]
        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COURSE_MAX_PAGE)
        serializer = MiniCourseSerializer(frame_pagination.get('results'), many=True,
                                          context={'profile': auth})

        frame_pagination['results'] = serializer.data
        return Response(frame_pagination, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_created_courses(self, request, path, *args, **kwargs):
        """Созданные курсы пользователем по path"""
        if not self.exists_profile_path(path):
            return Response({'error': "Такого пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)

        auth = Profile.objects.get(user=self.request.user)

        profile = Profile.objects.get(path=path)
        queryset = self.filter_queryset(self.queryset.filter(profile=profile))
        frame_pagination = self.get_frame_pagination(request, queryset, HelperPaginatorValue.MINI_COURSE_MAX_PAGE)
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

    @action(detail=False, methods=['delete'])
    def delete_course(self, request, path):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        course = self.queryset.get(path=path)
        MaxProgressUpdater.update_max_progress(old=course.max_progress, new=0, course=course)
        course.delete()
        return Response({
            'title': course.title,
            'path': course.path,
            'message': "Курс успешно удален"
        }, status=status.HTTP_200_OK)


class CoursePageView(viewsets.ModelViewSet):
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_page(self, request, path):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        course = Course.objects.get(path=path)
        course_info = CourseInfo.objects.get(course=course)
        serializer = EditPageInfoCourseSerializer(course_info)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def update_course(request, course_info):
        course = course_info.course
        validated_data = request.data.get('course', None)

        course.title = validated_data.get('title', course.title)
        course.description = validated_data.get('description', course.description)

        new_image = validated_data.get('image_url', -1)
        if new_image != -1:
            update_image = Util.get_image(old=course.image_url, new=new_image,
                                          default=Util.DEFAULT_IMAGES.get('course'))
            course.image_url = Util.get_update_image(old=course.image_url, new=update_image)

        course.save()
        return course

    @staticmethod
    def update_main_info(request, course_info):
        main_info = CourseMainInfo.objects.get(course_info=course_info)
        validated_data = request.data.get('main_info', None)

        main_info.goal_description = validated_data.get('goal_description', main_info.goal_description)

        new_image = validated_data.get('title_image_url', -1)
        if new_image != -1:
            main_info.image_url = Util.get_update_image(old=main_info.title_image_url, new=new_image)

        main_info.save()
        return main_info

    @staticmethod
    def update_fits(request, course_info):
        fit_list = CourseFit.objects.filter(course_info=course_info)
        validated_data = request.data.get('fits', None)
        for new_fit in validated_data:
            curr_fit = fit_list.filter(pk=new_fit.get('pk'))[0]
            curr_fit.title = new_fit.get('title', curr_fit.title)
            curr_fit.description = new_fit.get('description', curr_fit.description)
            curr_fit.save()
        return fit_list

    @staticmethod
    def update_skills(request, course_info):
        skill_list = CourseSkill.objects.filter(course_info=course_info)
        validated_data = request.data.get('skills', None)
        for new_skill in validated_data:
            curr_skill = skill_list.filter(pk=new_skill.get('pk'))[0]
            curr_skill.name = new_skill.get('name', curr_skill.name)
            curr_skill.save()
        return skill_list

    @action(detail=False, methods=['put'])
    def save_page(self, request, path):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        course = Course.objects.get(path=path)
        course_info = CourseInfo.objects.get(course=course)
        self.update_course(request=request, course_info=course_info)
        self.update_main_info(request=request, course_info=course_info)
        self.update_fits(request=request, course_info=course_info)
        self.update_skills(request=request, course_info=course_info)
        return Response({
            'message': "Успешно обновлено"
        }, status=status.HTTP_200_OK)


class CourseFitView(viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = CourseFit.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def exists(pk):
        return PathValidator.get_exists(data={'pk': pk}, model=CourseFit,
                                        error_text="Такого представителя не существует")

    @action(detail=False, methods=['post'])
    def create_fit(self, request, path):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        course = Course.objects.get(path=path)
        course_info = CourseInfo.objects.get(course=course)
        number_new = len(self.queryset.filter(course_info=course_info)) + 1
        data = {
            'title': f"Представитель #{number_new}",
            'description': f"Причина почему",
        }

        serializer = CourseFitSerializer(data=data, context={'course_info': course_info})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'pk': serializer.data['pk'],
            'title': serializer.data['title'],
            'description': serializer.data['description'],
            'message': "Представитель успешно создан",
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_fit(self, request, path):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        exists_fit = self.exists(pk=request.data.get('pk', None))
        if exists_fit.get('error', None) is not None:
            return exists_fit.get('error')

        fit = self.queryset.get(pk=request.data.get('pk'))
        serializer = CourseFitSerializer(data=request.data, instance=fit)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'pk': request.data.get('pk'),
            'title': fit.title,
            'description': fit.description,
            'message': "Представитель успешно обновлен"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_fit(self, request, path):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        exists_fit = self.exists(pk=request.data.get('pk', None))
        if exists_fit.get('error', None) is not None:
            return exists_fit.get('error')

        fit = self.queryset.get(pk=request.data.get('pk'))
        fit.delete()
        return Response({
            'pk': request.data.get('pk'),
            'title': fit.title,
            'description': fit.description,
            'message': "Представитель успешно удален"
        }, status=status.HTTP_200_OK)


class CourseSkillView(viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = CourseSkill.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def exists(pk):
        return PathValidator.get_exists(data={'pk': pk}, model=CourseSkill,
                                        error_text="Такого представителя не существует")

    @action(detail=False, methods=['post'])
    def create_skill(self, request, path):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        course = Course.objects.get(path=path)
        course_info = CourseInfo.objects.get(course=course)
        number_new = len(self.queryset.filter(course_info=course_info)) + 1
        data = {'name': f"Умение #{number_new}"}

        serializer = CourseSkillSerializer(data=data, context={'course_info': course_info})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'pk': serializer.data['pk'],
            'name': serializer.data['name'],
            'message': "Умение успешно создано",
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_skill(self, request, path):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        exists = self.exists(pk=request.data.get('pk', None))
        if exists.get('error', None) is not None:
            return exists.get('error')

        skill = self.queryset.get(pk=request.data.get('pk'))
        serializer = CourseSkillSerializer(data=request.data, instance=skill)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'pk': serializer.data['pk'],
            'name': serializer.data['name'],
            'message': "Умение успешно обновлено",
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_skill(self, request, path):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        exists = self.exists(pk=request.data.get('pk', None))
        if exists.get('error', None) is not None:
            return exists.get('error')

        skill = self.queryset.get(pk=request.data.get('pk'))
        skill.delete()
        return Response({
            'pk': request.data.get('pk'),
            'name': skill.name,
            'message': "Умение успешно удалено"
        }, status=status.HTTP_200_OK)


class CourseCompletionPageView(viewsets.ModelViewSet):
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]

    # PAGE THEMES
    @action(detail=False, methods=['get'])
    def get_title_course(self, request, path_course):
        exists = PathValidator.exists(path_course=path_course)
        if exists.get('error', None) is not None:
            return exists.get('error')

        course = Course.objects.get(path=path_course)
        serializer = CourseTitleSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_themes(self, request, path_course):
        exists = PathValidator.exists(path_course=path_course)
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
        exists = PathValidator.exists(path_course=path_course, path_theme=path_theme)
        if exists.get('error', None) is not None:
            return exists.get('error')

        theme = Theme.objects.get(path=path_theme)
        serializer = ThemeTitleSerializer(theme)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_lessons(self, request, path_course, path_theme):
        exists = PathValidator.exists(path_course=path_course, path_theme=path_theme)
        if exists.get('error', None) is not None:
            return exists.get('error')

        auth = Profile.objects.get(user=self.request.user)
        theme = Theme.objects.get(path=path_theme)
        lesson_list = Lesson.objects.filter(theme=theme)
        serializer = ProfileLessonSerializer(lesson_list, many=True, context={'profile': auth, 'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ###########

    # PAGE STEPS
    @action(detail=False, methods=['get'])
    def get_steps(self, request, path_course, path_theme, path_lesson, path_step):
        exists = PathValidator.exists(path_course=path_course, path_theme=path_theme, path_lesson=path_lesson,
                                      path_step=path_step)
        if exists.get('error', None) is not None:
            return exists.get('error')

        auth = Profile.objects.get(user=self.request.user)
        lesson = Lesson.objects.get(path=path_lesson)
        step_list = Step.objects.filter(lesson=lesson)
        current_step = step_list.get(path=path_step)
        serializer = GetStepSerializer(step_list, many=True,
                                       context={'profile': auth, 'current_step': current_step})

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def add_profile_action_logs(profile, step):
        if len(ProfileCourse.objects.filter(profile=profile, course=step.lesson.theme.course)) != 0:
            if len(ProfileStep.objects.filter(profile=profile, step=step)) != 0:
                if len(ProfileActionsLogs.objects.filter(profile=profile, step=step)) == 0:
                    profile_action_logs = ProfileActionsLogs.objects.create(profile=profile, step=step)
                    profile_action_logs.save()
                    return True
        return False

    @staticmethod
    def add_profile_step(profile, step):
        profile_step_list = ProfileStep.objects.filter(profile=profile, step=step)
        if len(profile_step_list) == 0:
            profile_step = ProfileStep.objects.create(profile=profile, step=step)
            profile_step.save()
        CourseCompletionPageView.add_profile_action_logs(profile=profile, step=step)

    @action(detail=False, methods=['get'])
    def get_detail_step(self, request, path_course, path_theme, path_lesson, path_step):
        exists = PathValidator.exists(path_course=path_course, path_theme=path_theme, path_lesson=path_lesson,
                                      path_step=path_step)
        if exists.get('error', None) is not None:
            return exists.get('error')

        auth = Profile.objects.get(user=self.request.user)
        step = Step.objects.get(path=path_step)
        serializer = StepSerializer(step, context={'profile': auth, 'request': request})

        self.add_profile_step(profile=auth, step=step)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def exists_profile_step(profile, step):
        profile_step_list = ProfileStep.objects.filter(profile=profile, step=step)
        if len(profile_step_list) == 0:
            raise ValidationError({'error': 'Вы не изучаете данный шаг'})
        return True

    @action(detail=False, methods=['put'])
    def complete_step(self, request, path_course, path_theme, path_lesson, path_step):
        exists = PathValidator.exists(path_course=path_course, path_theme=path_theme, path_lesson=path_lesson,
                                      path_step=path_step)
        if exists.get('error', None) is not None:
            return exists.get('error')

        auth = Profile.objects.get(user=self.request.user)
        step = Step.objects.get(path=path_step)

        self.exists_profile_step(profile=auth, step=step)
        profile_step = ProfileStep.objects.get(profile=auth, step=step)
        new_status = ProfileStepStatus.objects.filter(name=Util.PROFILE_COURSE_STATUS_STUDIED_NAME)[0]
        serializer = ProfileStepSerializer(instance=profile_step, data={}, context={'status': new_status})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.data)

        return Response({'message': "Вы успешно изучили step!"}, status=status.HTTP_200_OK)

    # ###########

    # COMPLETE COURSE
    @action(detail=False, methods=['post'])
    def start_learn_course(self, request, path):
        exists = PathValidator.exists(path_course=path)
        if exists.get('error', None) is not None:
            return exists.get('error')

        auth = Profile.objects.get(user=self.request.user)
        course = Course.objects.get(path=path)
        profile_course_list = ProfileCourse.objects.filter(course=course, profile=auth)
        if len(profile_course_list) == 0:
            profile_course_list = ProfileCourse.objects.create(course=course, profile=auth)
        profile_course = profile_course_list[0]
        profile_course.status = ProfileCourseStatus.objects.get(name=Util.PROFILE_COURSE_STATUS_STUDYING_NAME)
        profile_course.save()

        return Response({
            'profile': auth.user.username,
            'course': course.path,
            'status': profile_course.status.name,
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def complete_learn_course(self, request, path):
        exists = PathValidator.exists(path_course=path)
        if exists.get('error', None) is not None:
            return exists.get('error')

        auth = Profile.objects.get(user=self.request.user)
        course = Course.objects.get(path=path)
        profile_course_list = ProfileCourse.objects.filter(course=course, profile=auth)
        if len(profile_course_list) == 0:
            return Response({'error': "Вы не поступили на этот курс, чтобы завершить его"},
                            status=status.HTTP_400_BAD_REQUEST)
        profile_course = profile_course_list[0]
        profile_course.status = ProfileCourseStatus.objects.get(name=Util.PROFILE_COURSE_STATUS_STUDIED_NAME)
        profile_course.save()

        return Response({
            'profile': auth.user.username,
            'course': course.path,
            'status': profile_course.status.name,
        }, status=status.HTTP_200_OK)

    # ###########


class ThemeView(viewsets.ModelViewSet):
    """Тема"""
    lookup_field = 'slug'
    queryset = Theme.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_theme(self, request, path):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path)
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
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        course = Course.objects.get(path=path_course)
        theme = self.queryset.get(path=path_theme)
        serializer = ActionThemeSerializer(theme, context={'course': course})

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_theme(self, request, path_course, path_theme):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
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
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        theme = self.queryset.get(path=path_theme)
        MaxProgressUpdater.update_max_progress(old=theme.max_progress, new=0, theme=theme)
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
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
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
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme,
                                          path_lesson=path_lesson)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        theme = Theme.objects.get(path=path_theme)
        lesson = self.queryset.get(path=path_lesson)
        serializer = ActionLessonSerializer(lesson, context={'theme': theme})

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_lesson(self, request, path_course, path_theme, path_lesson):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
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
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        lesson = self.queryset.get(path=path_lesson)
        MaxProgressUpdater.update_max_progress(old=lesson.max_progress, new=0, lesson=lesson)
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
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme,
                                          path_lesson=path_lesson)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        lesson = Lesson.objects.get(path=path_lesson)
        number_new_step = len(self.queryset.filter(lesson=lesson)) + 1
        serializer = ActionStepSerializer(data={'title': f"Шаг #{number_new_step}"},
                                          context={'lesson': lesson, 'number': number_new_step})
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
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme,
                                          path_lesson=path_lesson, path_step=path_step)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        lesson = Lesson.objects.get(path=path_lesson)
        step = self.queryset.get(path=path_step)
        serializer = StepSerializer(step, context={'lesson': lesson})

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_step(self, request, path_course, path_theme, path_lesson, path_step):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme,
                                          path_lesson=path_lesson, path_step=path_step)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        step = self.queryset.get(path=path_step)
        serializer = ActionStepSerializer(data=request.data, instance=step, context={'step': step})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_step(self, request, path_course, path_theme, path_lesson, path_step):
        is_valid = PathValidator.is_valid(user=self.request.user, path_course=path_course, path_theme=path_theme,
                                          path_lesson=path_lesson, path_step=path_step)
        if is_valid.get('error', None) is not None:
            return is_valid.get('error')

        step = self.queryset.get(path=path_step)
        MaxProgressUpdater.update_max_progress(old=step.max_progress, new=0, step=step)
        step.delete()
        ActionStepSerializer.update_numbers(step_list=Step.objects.filter(lesson=step.lesson))
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


class PathValidator:

    @staticmethod
    def get_exists(data, model, error_text):
        if data is not None:
            if not Util.exists_path(model, validated_data=data):
                return {
                    'valid': False,
                    'error': Response({'error': error_text}, status=status.HTTP_404_NOT_FOUND),
                }
        return {'valid': True}

    @staticmethod
    def is_valid(user=None, path_course=None, path_theme=None, path_lesson=None, path_step=None):
        if user is not None:
            is_access = PathValidator.is_access(user=user, path_course=path_course)
            if is_access.get('error', None) is not None:
                return is_access

        exists = PathValidator.exists(path_course=path_course, path_theme=path_theme, path_lesson=path_lesson,
                                      path_step=path_step)
        if exists.get('error', None) is not None:
            return exists
        return {'valid': True}

    @staticmethod
    def exists(path_course=None, path_theme=None, path_lesson=None, path_step=None):
        if path_course is not None:
            exists_course = PathValidator.exists_course(path_course=path_course)
            if exists_course.get('error', None) is not None:
                return exists_course

        if path_theme is not None:
            exists_theme = PathValidator.exists_theme(path_theme=path_theme)
            if exists_theme.get('error', None) is not None:
                return exists_theme

        if path_lesson is not None:
            exists_lesson = PathValidator.exists_lesson(path_lesson=path_lesson)
            if exists_lesson.get('error', None) is not None:
                return exists_lesson

        if path_step is not None:
            exists_step = PathValidator.exists_step(path_step=path_step)
            if exists_step.get('error', None) is not None:
                return exists_step

        return {'valid': True}

    @staticmethod
    def exists_course(path_course):
        return PathValidator.get_exists(data={'path': path_course}, model=Course,
                                        error_text="Такого курса не существует")

    @staticmethod
    def exists_theme(path_theme):
        return PathValidator.get_exists(data={'path': path_theme}, model=Theme, error_text="Такой темы не существует")

    @staticmethod
    def exists_lesson(path_lesson):
        return PathValidator.get_exists(data={'path': path_lesson}, model=Lesson,
                                        error_text="Такого урока не существует")

    @staticmethod
    def exists_step(path_step):
        return PathValidator.get_exists(data={'path': path_step}, model=Step, error_text="Такого шага не существует")

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
