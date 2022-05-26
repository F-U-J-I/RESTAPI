from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('', include('core.auth.urls_auth')),
    path('', include('core.course.urls_course')),
    path('', include('core.collection.urls_collection')),
    path('', include('core.profile.urls_profile')),
]
