from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_profile import ProfileView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('profile/<slug:path>/', ProfileView.as_view()),
]
