from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_course import CourseView, GradeCourseView, ActionProfileCourseView, ActionCourseView, ThemeView, LessonView, \
    StepView, CourseCompletionPage

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    # GET
    path('courses/', CourseView.as_view({'get': 'get_courses'})),
    path('mini-courses/', CourseView.as_view({'get': 'get_mini_courses'})),
    path('courses/all/<slug:path>/', CourseView.as_view({'get': 'get_all_profile_courses'})),
    path('courses/added/<slug:path>/', CourseView.as_view({'get': 'get_added_courses'})),
    path('courses/created/<slug:path>/', CourseView.as_view({'get': 'get_created_courses'})),
    path('courses/page/<slug:path>/', CourseView.as_view({'get': 'get_page_course'})),

    # GRADE
    path('courses/create/grade/<slug:path>/', GradeCourseView.as_view({'post': 'set_grade'})),
    path('courses/update/grade/<slug:path>/', GradeCourseView.as_view({'put': 'update_grade'})),
    path('courses/delete/grade/<slug:path>/', GradeCourseView.as_view({'delete': 'delete_grade'})),

    # COURSE
    path('courses/create/', ActionCourseView.as_view({'post': 'create_course'})),
    path('courses/learn/<slug:path>/', CourseCompletionPage.as_view({'post': 'take_course'})),

    # COURSE completion
    path('courses/learn/<slug:path_course>/title/',
         CourseCompletionPage.as_view({'get': 'get_title_course'})),
    path('courses/learn/<slug:path_course>/themes/',
         CourseCompletionPage.as_view({'get': 'get_themes'})),
    path('courses/learn/<slug:path_course>/theme/<slug:path_theme>/title/',
         CourseCompletionPage.as_view({'get': 'get_title_theme'})),
    path('courses/learn/<slug:path_course>/theme/<slug:path_theme>/lessons/',
         CourseCompletionPage.as_view({'get': 'get_lessons'})),
    path('courses/learn/<slug:path_course>/theme/<slug:path_theme>/lesson/<slug:path_lesson>/steps/<slug:path_step>/list/',
         CourseCompletionPage.as_view({'get': 'get_steps'})),
    path('courses/learn/<slug:path_course>/theme/<slug:path_theme>/lesson/<slug:path_lesson>/steps/<slug:path_step>/',
         CourseCompletionPage.as_view({'get': 'get_detail_step'})),

    # THEME
    path('courses/creating/<slug:path>/create/theme/',
         ThemeView.as_view({'post': 'create_theme'})),
    path('courses/creating/<slug:path_course>/get-update/theme/<slug:path_theme>/',
         ThemeView.as_view({'get': 'get_update_info'})),
    path('courses/creating/<slug:path_course>/update/theme/<slug:path_theme>/',
         ThemeView.as_view({'put': 'update_theme'})),
    path('courses/creating/<slug:path_course>/delete/theme/<slug:path_theme>/',
         ThemeView.as_view({'delete': 'delete_theme'})),

    # LESSON
    path('courses/creating/<slug:path_course>/theme/<slug:path_theme>/create/lesson/',
         LessonView.as_view({'post': 'create_lesson'})),
    path('courses/creating/<slug:path_course>/theme/<slug:path_theme>/get-update/lesson/<slug:path_lesson>/',
         LessonView.as_view({'get': 'get_update_info'})),
    path('courses/creating/<slug:path_course>/theme/<slug:path_theme>/update/lesson/<slug:path_lesson>/',
         LessonView.as_view({'put': 'update_lesson'})),
    path('courses/creating/<slug:path_course>/theme/<slug:path_theme>/delete/lesson/<slug:path_lesson>/',
         LessonView.as_view({'delete': 'delete_lesson'})),

    # STEP
    path('courses/creating/<slug:path_course>/theme/<slug:path_theme>/lesson/<slug:path_lesson>/create/step/',
         StepView.as_view({'post': 'create_step'})),
    path(
        'courses/creating/<slug:path_course>/theme/<slug:path_theme>/lesson/<slug:path_lesson>/get-update/step/<slug:path_step>',
        StepView.as_view({'get': 'get_update_info'})),
    path(
        'courses/creating/<slug:path_course>/theme/<slug:path_theme>/lesson/<slug:path_lesson>/update/step/<slug:path_step>',
        StepView.as_view({'put': 'update_step'})),
    path(
        'courses/creating/<slug:path_course>/theme/<slug:path_theme>/lesson/<slug:path_lesson>/delete/step/<slug:path_step>',
        StepView.as_view({'delete': 'delete_step'})),

    path('courses/add/<slug:path>/', ActionProfileCourseView.as_view({'post': 'added_courses'})),
    path('courses/pop/<slug:path>/', ActionProfileCourseView.as_view({'delete': 'popped_courses'})),
]
