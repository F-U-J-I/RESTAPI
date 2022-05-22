from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, ProfileView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view()),
    path('profile/<slug:path>/', ProfileView.as_view()),
]