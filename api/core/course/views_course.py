from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models_course import Course, CourseInfo, ProfileCourse
from .serializers_course import GradeCourseSerializer, PageCourseSerializer, PageInfoCourseSerializer, CourseSerializer
from ..profile.models_profile import Profile


class CourseView(viewsets.ModelViewSet):
    """Курсы"""
    lookup_field = 'slug'
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def exists_path(self, path):
        return len(self.queryset.filter(path=path)) != 0

    @action(methods=['get'], detail=False)
    def get_list_course(self, request, *args, **kwargs):
        serializer_course_list = list()
        profile = Profile.objects.get(user=self.request.user)
        for course in self.queryset:
            serializer_course_list.append(
                CourseSerializer(course, context={'profile': profile}).data)
        return Response(serializer_course_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_list_mini_course(self, request, *args, **kwargs):
        serializer_course_list = list()
        profile = Profile.objects.get(user=self.request.user)
        for course in self.queryset:
            serializer_course_list.append(
                CourseSerializer(course, context={'profile': profile}).data)
        return Response(serializer_course_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def get_page_course(self, request, path, *args, **kwargs):
        if not self.exists_path(path):
            return Response({'error': "Такого курса не существует"}, status=status.HTTP_404_NOT_FOUND)

        course = self.queryset.get(path=path)
        profile = Profile.objects.get(user=request.user)
        serializer_course = PageCourseSerializer(course, context={'profile': profile})

        course_info = CourseInfo.objects.get(course=course)
        serializer_course_info = PageInfoCourseSerializer(course_info, context={'profile': profile})
        return Response(data={
            'course': serializer_course.data,
            'info': serializer_course_info.data
        }, status=status.HTTP_200_OK)

    # #########################################
    #        ######## GRADE ########
    # #########################################

    @action(detail=False, methods=['post'])
    def set_grade(self, request, path):
        if not self.exists_path(path):
            return Response({'error': "Такого курса не существует"}, status=status.HTTP_404_NOT_FOUND)

        course = self.queryset.get(path=path)
        profile = Profile.objects.get(user=self.request.user)
        serializer = GradeCourseSerializer(data=request.data, context={'profile': profile, 'course': course})
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception:
            return Response({'error': "Вы уже оценивали этот курс"}, status=status.HTTP_400_BAD_REQUEST)
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
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({'error': "Вы уже оценивали этот курс"}, status=status.HTTP_400_BAD_REQUEST)
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

    # TODO: Сделать изменение страницы курса
    # TODO: Сделать изменение курса
