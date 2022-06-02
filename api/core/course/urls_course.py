from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_course import CourseView, GradeCourseView, ActionProfileCourseView, ActionCourseView, ThemeView, LessonView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('courses/', CourseView.as_view({'get': 'get_courses'})),
    path('mini-courses/', CourseView.as_view({'get': 'get_mini_courses'})),
    path('courses/all/<slug:path>/', CourseView.as_view({'get': 'get_all_profile_courses'})),
    path('courses/added/<slug:path>/', CourseView.as_view({'get': 'get_added_courses'})),
    path('courses/created/<slug:path>/', CourseView.as_view({'get': 'get_created_courses'})),
    path('courses/page/<slug:path>/', CourseView.as_view({'get': 'get_page_course'})),

    path('courses/create/grade/<slug:path>/', GradeCourseView.as_view({'post': 'set_grade'})),
    path('courses/update/grade/<slug:path>/', GradeCourseView.as_view({'put': 'update_grade'})),
    path('courses/delete/grade/<slug:path>/', GradeCourseView.as_view({'delete': 'delete_grade'})),

    path('courses/create/', ActionCourseView.as_view({'post': 'create_course'})),

    # THEME
    path('courses/creating/<slug:path>/create/theme/', ThemeView.as_view({'post': 'create_theme'})),
    path('courses/creating/<slug:path_course>/get-update/theme/<slug:path_theme>/', ThemeView.as_view({'get': 'get_update_info'})),
    path('courses/creating/<slug:path_course>/update/theme/<slug:path_theme>/', ThemeView.as_view({'put': 'update_theme'})),
    path('courses/creating/<slug:path_course>/delete/theme/<slug:path_theme>/', ThemeView.as_view({'delete': 'delete_theme'})),

    # LESSON
    path('courses/creating/<slug:path_course>/theme/<slug:path_theme>/create/lesson/', LessonView.as_view({'post': 'create_lesson'})),

    path('courses/add/<slug:path>/', ActionProfileCourseView.as_view({'post': 'added_courses'})),
    path('courses/pop/<slug:path>/', ActionProfileCourseView.as_view({'delete': 'popped_courses'})),
]
