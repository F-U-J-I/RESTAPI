from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_course import CourseView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('courses/', CourseView.as_view({'get': 'get_list_course'})),
    path('mini-courses/', CourseView.as_view({'get': 'get_list_mini_course'})),
    path('courses/page/<slug:path>/', CourseView.as_view({'get': 'get_page_course'})),
]