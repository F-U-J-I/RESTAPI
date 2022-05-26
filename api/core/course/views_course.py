from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers_course as serializers
from .models_course import Course, CourseInfo
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
                serializers.CourseSerializer(course, context={'profile': profile}).data)
        return Response(serializer_course_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_list_mini_course(self, request, *args, **kwargs):
        serializer_course_list = list()
        profile = Profile.objects.get(user=self.request.user)
        for course in self.queryset:
            serializer_course_list.append(
                serializers.CourseSerializer(course, context={'profile': profile}).data)
        return Response(serializer_course_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def get_page_course(self, request, path, *args, **kwargs):
        if not self.exists_path(path):
            return Response({'error': "Такого курса не существует"}, status=status.HTTP_404_NOT_FOUND)

        course = self.queryset.get(path=path)
        profile = Profile.objects.get(user=request.user)
        serializer_course = serializers.PageCourseSerializer(course, context={'profile': profile})

        course_info = CourseInfo.objects.get(course=course)
        serializer_course_info = serializers.PageInfoCourseSerializer(course_info, context={'profile': profile})
        return Response(data={
            'course': serializer_course.data,
            'info': serializer_course_info.data
        }, status=status.HTTP_200_OK)

    # TODO: Подборкам. Выставление оценки
    # TODO: Курсам. Выставление оценки
    # TODO: Сделать изменение страницы курса
    # TODO: Сделать изменение курса
