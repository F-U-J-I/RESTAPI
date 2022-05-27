from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_profile import ProfileView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('profiles/', ProfileView.as_view({'get': 'get_list_profile'})),
    path('mini-profiles/', ProfileView.as_view({'get': 'get_list_mini_profile'})),
    path('profiles/<slug:path>/studying/courses/', ProfileView.as_view({'get': 'get_studying_courses'})),
    # path('profile/<slug:path>/', ProfileView.as_view()),
]
