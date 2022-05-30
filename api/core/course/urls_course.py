from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_course import CourseView, GradeCourseView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('courses/', CourseView.as_view({'get': 'get_courses'})),
    path('mini-courses/', CourseView.as_view({'get': 'get_mini_courses'})),
    path('courses/all/<slug:path>/', CourseView.as_view({'get': 'get_profile_courses'})),
    path('courses/added/<slug:path>/', CourseView.as_view({'get': 'get_added_courses'})),
    path('courses/created/<slug:path>/', CourseView.as_view({'get': 'get_created_courses'})),
    path('courses/page/<slug:path>/', CourseView.as_view({'get': 'get_page_course'})),

    path('courses/create/grade/<slug:path>/', GradeCourseView.as_view({'post': 'set_grade'})),
    path('courses/update/grade/<slug:path>/', GradeCourseView.as_view({'put': 'update_grade'})),
    path('courses/delete/grade/<slug:path>/', GradeCourseView.as_view({'delete': 'delete_grade'})),
]
